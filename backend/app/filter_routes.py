#filter_routes.py

import redis
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload
from fastapi.encoders import jsonable_encoder
from geoalchemy2.functions import ST_DWithin, ST_Point
from typing import Optional

from datetime import date
import math

from .models import NumerologyReport, NumerologyReportAuth, SubReport

from .schemas import *
from .database import get_db, get_redis_client
from .limiter import limiter

import json
import hashlib

router = APIRouter()

def generate_cache_key(route: str, params: dict) -> str:
    """
    Generates a cache key by removing null values and hashing the query parameters.
    """
    filtered_params = {k: v for k, v in params.items() if v is not None}  # Remove null values
    key_string = route + json.dumps(filtered_params, sort_keys=True)
    return hashlib.md5(key_string.encode()).hexdigest()

# Adjust TTL dynamically
def determine_ttl(filters: dict) -> int:
    if filters.get("birthday") or filters.get("age") or filters.get('personName') or filters.get('gender') or filters.get('haveInstagram'):
        return 30  # 1 minute
    return 80  # Default 5 minutes


@router.get("/freports")
@limiter.limit("16/minute")
async def read_public_reports_filter(
    request: Request,
    db: Session = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis_client),
    limit: int = Query(10, ge=1),
    offset: int = Query(0, ge=0),
    gender: Optional[str] = Query(None),
    haveInstagram: bool = Query(False),
    personName: Optional[str] = Query(None),
    uniqueSubReport: bool = Query(False),
    includePublic: bool = Query(False),
    latitude: Optional[float] = Query(None),
    longitude: Optional[float] = Query(None),
    radius: Optional[int] = Query(None),
    age: Optional[int] = Query(None),
    splitPercentage: Optional[int] = Query(50),  # Default: 70% private, 30% public
    birthday: Optional[str] = Query(None),  
):
    # Generate cache key without null values
    cache_key = generate_cache_key("/freports", {
        "limit": limit, "offset": offset, "gender": gender,
        "haveInstagram": haveInstagram, "personName": personName,
        "uniqueSubReport": uniqueSubReport, "includePublic": includePublic,
        "latitude": latitude, "longitude": longitude,
        "radius": radius, "age": age, "birthday": birthday
    })

    try:
        cached_response = redis_client.get(cache_key)
        if cached_response:
            # print("redis_cached_res")
            return json.loads(cached_response)
    except Exception as e:
        print("Redis unavailable, falling back to database.",str(e))

    # Fetch filtered reports
    response_data = await get_public_reports_filter(
        db, redis_client, limit, offset, gender, haveInstagram, personName,
        uniqueSubReport, includePublic, latitude, longitude, radius, age,
        splitPercentage, birthday
    )
    try:
        filter = {
            "limit": limit, "offset": offset, "gender": gender,
            "haveInstagram": haveInstagram, "personName": personName,
            "uniqueSubReport": uniqueSubReport, "includePublic": includePublic,
            "latitude": latitude, "longitude": longitude,
            "radius": radius, "age": age, "splitPercentage": splitPercentage,
            "birthday": birthday
        }
        redis_client.setex(cache_key, determine_ttl(filter), json.dumps(response_data))
    except Exception as e:
        print("Failed to write to Redis cache.", str(e))
    
    return response_data



async def get_public_reports_filter(
    db: Session,
    redis_client: redis.Redis,
    limit: int,
    offset: int,
    gender: Optional[str] = None,
    haveInstagram: bool = False,
    personName: Optional[str] = None,
    uniqueSubReport: bool = False,
    includePublic: bool = False,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    radius: Optional[int] = None,
    minAge: Optional[int] = None,
    splitPercentage: Optional[int] = 50,  # Default to 70% private, 30% public
    birthday: Optional[str] = None,   
):
    """
    Fetch paginated reports with applied filters and caching for counts.
    """
    # Calculate minimum date of birth for age filtering
    min_dob = date.today().replace(year=date.today().year - minAge) if minAge else None

    def apply_common_conditions(query, is_auth_report: bool):
        """
        Applies common conditions to filter the query for both authorized and public reports.
        """
        if gender:
            gender_field = (
                func.lower(NumerologyReportAuth.report_data["person_info"]["gender"].astext)
                if is_auth_report else func.lower(SubReport.gender)
            )
            query = query.filter(gender_field == gender.lower())

        if haveInstagram:
            instagram_filter = (
                NumerologyReportAuth.instagram_username.isnot(None)
                if is_auth_report else NumerologyReport.instagram_username.isnot(None)
            )
            query = query.filter(instagram_filter)

        if min_dob:
            dob_field = (
                func.to_date(NumerologyReportAuth.report_data["person_info"]["dob"].astext, "YYYY-MM-DD")
                if is_auth_report else func.to_date(SubReport.report_data["person_info"]["dob"].astext, "YYYY-MM-DD")
            )
            query = query.filter(dob_field >= min_dob) #return more then or equal to given age

        if personName:
            name_field = (
                func.lower(NumerologyReportAuth.report_data["person_info"]["name"].astext)
                if is_auth_report else func.lower(NumerologyReport.person_name)
            )
            query = query.filter(name_field.contains(personName.lower()))

        if birthday:
            dob_field = (
                NumerologyReportAuth.report_data["person_info"]["dob"].astext
                if is_auth_report else SubReport.report_data["person_info"]["dob"].astext
            )
            query = query.filter(
                func.to_char(func.to_date(dob_field, "YYYY-MM-DD"), "MM-DD") ==
                func.to_char(func.to_date(birthday, "YYYY-MM-DD"), "MM-DD")
            )

        if is_auth_report:
            query = query.filter(NumerologyReportAuth.is_public.is_(True))
        else:
            query = query.filter(NumerologyReport.is_public.is_(True))

        return query

    
    # Correct offset and limit allocation
    
    # Determine split dynamically based on splitPercentage
    splitPercentage = max(0, min(splitPercentage, 100)) if includePublic else 100  # Clamp to [0, 100] and only split if including public reports
    auth_limit = math.ceil(limit * (splitPercentage / 100)) 
    public_limit = limit - auth_limit

    #  offsets (when user gets large then it may fit well)
    # auth_offset = offset-public_limit if auth_limit < limit else offset
    # public_offset = max(offset - auth_limit, 0) if auth_limit < limit else offset - public_limit

    # Adjust offsets for each query part based on the split
    auth_offset = max(0, offset)  # Offset for authorized reports
    public_offset = max(0, offset - auth_limit)  # Offset for public reports, adjusted by the auth_limit


    # Query for authorized reports
    auth_query = db.query(NumerologyReportAuth).options(
        joinedload(NumerologyReportAuth.auth_user)
    )
    if latitude and longitude and radius:
        auth_query = auth_query.join(AuthUser).filter(
            ST_DWithin(
                AuthUser.location,
                ST_Point(longitude, latitude),
                radius * 1000  # Converting to meters
            )
        )
    auth_query = apply_common_conditions(auth_query, is_auth_report=True)
    auth_query = auth_query.order_by(NumerologyReportAuth.created_at.desc())
    auth_reports = auth_query.offset(auth_offset).limit(auth_limit).all()

    # Query for public reports
    public_reports = []
    if includePublic:
        public_query = db.query(NumerologyReport)
        if uniqueSubReport or birthday or minAge or gender:
            public_query = public_query.join(
                SubReport, NumerologyReport.sub_report_id == SubReport.id
            )
        if uniqueSubReport:
            public_query = public_query.distinct(NumerologyReport.sub_report_id).order_by(
                NumerologyReport.sub_report_id, NumerologyReport.created_at.desc()
            )
        else:
            public_query = public_query.order_by(NumerologyReport.created_at.desc())

        public_query = apply_common_conditions(public_query, is_auth_report=False)
        public_reports = public_query.offset(public_offset).limit(public_limit).all()

    # Combine results
    combined_reports = auth_reports + public_reports
    if any([gender, haveInstagram, personName,
            uniqueSubReport, latitude, minAge,
            birthday]
        ):
        total_reports = len(combined_reports)
    else:
        # Pre-calculate total counts with caching
        try:
            total_auth_reports = redis_client.get("total_auth_reports")
            if total_auth_reports is None:
                total_auth_reports = db.query(NumerologyReportAuth).count()
                redis_client.setex("total_auth_reports", 1800, total_auth_reports)  # Cache for 5 minutes
            else:
                total_auth_reports = int(total_auth_reports)

            total_public_reports = redis_client.get("total_public_reports")
            if total_public_reports is None:
                total_public_reports = db.query(NumerologyReport).count()
                redis_client.setex("total_public_reports", 1800, total_public_reports)  # Cache for 5 minutes
            else:
                total_public_reports = int(total_public_reports)
            
            total_reports = total_auth_reports + total_public_reports
        except Exception as e:
            print("Redis unavailable, simple total,.",str(e))
            total_reports = len(combined_reports)
        

    # Prepare response data
    data = [
        {
            "report_id": str(r.id),
            "id": str(r.user_id) if isinstance(r, NumerologyReportAuth) else "",
            "report_data": {
                "person_info": (
                    {**r.sub_report.report_data.get("person_info", {}), "name": r.person_name}
                    if isinstance(r, NumerologyReport) else
                    {**r.report_data.get("person_info", {}), "name": r.report_data["person_info"].get("name")}
                )
            },
            "is_auth_user": isinstance(r, NumerologyReportAuth),
            "instagram": r.instagram_username,
            "rating": r.rating,
            "is_public": r.is_public,
            "created_at": r.created_at,
            "picture": r.auth_user.picture if isinstance(r, NumerologyReportAuth) else "",
        }
        for r in combined_reports
    ]

    # Return response with corrected pagination info
    return {
        "data": jsonable_encoder(data),
        "total_reports": total_reports,
        "total_pages": (total_reports + limit - 1) // limit,
    }
