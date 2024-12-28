#controllers.py
# from .database import SessionLocal
import json
from uuid import UUID
from fastapi import HTTPException
from .models import (
    NumerologyReport, User, SubReport, 
    ReportIssues, CompatibilityReport, 
    SubMatch, AuthUser, NumerologyReportAuth
    )
from backend.utils.Numerology import Person
from sqlalchemy.orm import Session

from .jwt import create_jwt_token

# --------------------- COMPATIBILITY ---------------


def get_or_create_user(name: str, dob: str, gender: str, db: Session):
    """Helper function to get or create a user."""
    user = db.query(User).filter(
        User.name == name, User.dob == dob, User.gender == gender
    ).first()

    if not user:
        user = User(name=name, dob=dob, gender=gender)
        db.add(user)
        db.commit()
        # db.refresh(user)
    return user

async def get_match(match_id: UUID, db: Session):
    # Step 1: Retrieve the CompatibilityReport using match_id
    report = db.query(CompatibilityReport).filter(
        CompatibilityReport.id == match_id
    ).first()

    if not report:
        raise HTTPException(status_code=404, detail="Compatibility report not found")

    # Step 2: Retrieve users involved
    user1 = db.query(User).filter(User.id == report.user1_id).first()
    user2 = db.query(User).filter(User.id == report.user2_id).first()

    if not user1 or not user2:
        raise HTTPException(status_code=404, detail="One or both users not found")

    # Step 3: Retrieve SubMatch data
    sub_match = db.query(SubMatch).filter(SubMatch.id == report.sub_match_id).first()

    if not sub_match:
        raise HTTPException(status_code=404, detail="Sub-match data not found")

    # Use the names from the CompatibilityReport (if available) to override user names
    name1 = report.person1_name or user1.name
    name2 = report.person2_name or user2.name

    # Prepare the response data
    return {
        "match_id": str(report.id),
        "person_1": {
            "name": name1,
            "dob": user1.dob,
            "gender": user1.gender
        },
        "person_2": {
            "name": name2,
            "dob": user2.dob,
            "gender": user2.gender
        },
        "match_data": sub_match.match_data,
        "created_at": report.created_at
    }
    
async def compute_match_data(p1, p2):
    """Placeholder function to compute compatibility match data."""
    
    # Replace this with your logic for compatibility scoring and data generation
    op1 = Person(p1.dob, p1.gender, p1.name)
    op2 = Person(p2.dob, p2.gender, p2.name)
    c_data = op1.get_compatibility_data(op2)
    return c_data
    
    
async def generate_compatibility_report(match_request, db: Session):
    try:
        # Extracting person data
        p1 = match_request.person_1
        p2 = match_request.person_2

        # Step 1: Fetch or create users
        user1 = get_or_create_user(p1.name, p1.dob, p1.gender, db)
        user2 = get_or_create_user(p2.name, p2.dob, p2.gender, db)

        # Ensure the same user IDs are stored consistently (e.g., user1_id < user2_id)
        user1_id, user2_id = sorted([user1.id, user2.id])

        # Step 2: Check if SubMatch already exists for the given DOB and gender combination
        existing_sub_match = db.query(SubMatch).filter(
            SubMatch.dob1 == p1.dob, SubMatch.gender1 == p1.gender,
            SubMatch.dob2 == p2.dob, SubMatch.gender2 == p2.gender
        ).first()

        if existing_sub_match:
            print(f"Using existing SubMatch: {existing_sub_match.id}")
            sub_match = existing_sub_match
            # match_data = json.loads(sub_match.match_data)
            match_data = sub_match.match_data
        else:
            # Generate new match data
            match_data = await compute_match_data(p1, p2) 
            sub_match = SubMatch(
                dob1=p1.dob, gender1=p1.gender,
                dob2=p2.dob, gender2=p2.gender,
                match_data=match_data
            )
            db.add(sub_match)
            db.commit()
            # db.refresh(sub_match)
 
        # Step 3: Create the CompatibilityReport
        new_report = CompatibilityReport(
            user1_id=user1_id, user2_id=user2_id,
            person1_name=p1.name, person2_name=p2.name,
            sub_match_id=sub_match.id
        )
        db.add(new_report)
        db.commit()
        # db.refresh(new_report)
        # print(p1, p2,user1, user2,user1.gender, user2.gender )

        # Step 4: Prepare the response
        return {
            "match_id": str(new_report.id),
            "match_data": match_data,
            "created_at": new_report.created_at
        }
    except Exception as ex:
        # print("MatchExc:",ex)
        raise HTTPException(status_code=500, detail=f"Failed to create compatibility report: {ex}")
    

async def remove_match(match_id: UUID, db: Session):
    report = db.query(CompatibilityReport).filter(CompatibilityReport.id == match_id).first()

    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # rep = db.query(SubMatch).filter(SubMatch.id == report.sub_match_id).first()
    # db.delete(rep)  
    db.delete(report)
    db.commit()
    return {"message": "Report removed successfully"}


# --------------numerology reports --------------

from .schemas import ReportCreate, SavedReportIDs

async def generate_report(report : ReportCreate,  db: Session):
    name= report.name
    dob = report.dob
    gender = report.gender
    auth0_id = report.auth0_id
    
    name = name.capitalize()
    gender = gender.capitalize()

    # Check if a user already exists    
    existing_user = db.query(User).filter(
        # User.name == name,
        User.dob == dob,
        User.gender == gender,
    ).first()
    
    if existing_user:
        new_user = existing_user
        # print("Using existing user:", new_user.id)
    else:
        # Create a new User object
        new_user = User(name=name, dob=dob, gender=gender)
        db.add(new_user)
        db.commit()
        
    # Check if a report already exists with the same dob and gender

    existing_report = db.query(SubReport).filter(
        SubReport.dob == dob,
        SubReport.gender == gender
    ).first()
    
    if existing_report:
        sub_report = existing_report
        # print("Using existing report:", sub_report.id)
                
        # replace the name with current user, 
        # modified_report_data  = json.loads(sub_report.report_data)
        modified_report_data  = sub_report.report_data
        modified_report_data["person_info"]["name"] = name
        # print("modif 188",modified_report_data)
    else:
        try:
            # person_obj = Person(dob, gender, name, is_include_namaank=True)
            # not including namaank for public user as it would increase dependency=&=storage
            person_obj = Person(dob, gender, name)
            report_data = person_obj.get_all_data()
        except Exception as e:
            # print("Error while creating Report!",str(e))
            raise HTTPException(status_code=404, detail=f"Error while creating Report!, {str(e)}")

        # Create a new SubReport object  
        sub_report = SubReport(report_data=report_data, dob=dob, gender=gender)
        db.add(sub_report)
        db.commit()

    # print("previous-Commits :",new_user.id,sub_report.id)
    # Now make refer to above report_data
    is_temp = False if auth0_id else True
    
    new_report = NumerologyReport(user_id=new_user.id, sub_report_id=sub_report.id, person_name = name, is_temporary = is_temp)
    db.add(new_report)
    
    db.commit()
    
    if auth0_id:
        existing_auth_user = db.query(AuthUser).filter(AuthUser.auth0_id == auth0_id).first()

        # Ensure n_reports is initialized (empty list if None)
        if existing_auth_user.n_reports is None:
            existing_auth_user.n_reports = []

        # Append the new report ID to the list
        existing_auth_user.n_reports.append(str(new_report.id))  # new_report.id is the UUID

        # Commit the changes to the database
        db.commit()
    
    # Create JWT token for this report (with 5-month expiration)
    n_report_data = {"report_id": str(new_report.id)}
    token = create_jwt_token(n_report_data)

    # Prepare the modified report data for the response
    # modified_report_data_json = modified_report_data if existing_report else report_data
    # modified_report_data_json = json.dumps(modified_report_data) if existing_report else report_data

    return {
        "report_id": str(new_report.id),   
        "token": token,
        "user_data" :{
            "report_data": modified_report_data if existing_report else report_data,
            "is_authorized": True ,
            "is_auth_user": False,
            "is_temporary": is_temp,
            "instagram": None,
            "is_public": True,
            "rating": 3,
            "created_at":new_report.created_at
        },
    }


async def get_report(report_id : UUID, db: Session, payload):
    report = db.query(NumerologyReport).filter(NumerologyReport.id == report_id).first()
    if report is None:
        report = db.query(NumerologyReportAuth).filter(NumerologyReportAuth.id == report_id).first()

    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # Check if the user is authorized (only if payload is not None)
    is_authorized = False
    if payload:
        is_authorized =  str(report.id) == payload.get('report_id')
    
    if report.rating == 0:
        raise HTTPException(status_code=404, detail="Not Found")

    if isinstance(report, NumerologyReportAuth):
        report_data = report.report_data
    elif isinstance(report, NumerologyReport):
        sub_report = report.sub_report
        if not sub_report:
            user = db.query(User).filter(User.id == report.user_id).first()
            if user:       
                person_obj = Person(user.dob, user.gender, user.name)
                report_data = person_obj.get_all_data()
        else:
            # Parse the JSON report data
            try:
                report_data = sub_report.report_data
                # report_data = json.loads(sub_report.report_data)
                # replace the name in the sub_report data 
                report_data['person_info']['name'] = report.person_name
                # report_data = report_data
                # report_data = json.dumps(report_data)
            except json.JSONDecodeError:
                raise HTTPException(status_code=500, detail="Invalid report data format")
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error occured in report_data, {str(e)}")
            
    response_data = {
        "report_id":report_id,
        "user_data": {
            "report_data": report_data, 
            "is_authorized": is_authorized,
            "is_auth_user": isinstance(report, NumerologyReportAuth),
            "summary": report.summary if isinstance(report, NumerologyReportAuth) else None,
            "is_temporary":report.is_temporary if isinstance(report, NumerologyReport) else False,
            "instagram": report.instagram_username,
            "is_public": report.is_public,
            "rating": report.rating
        }
    }
        
    return response_data

async def get_report_setAuth(auth0_user, data: SavedReportIDs, db: Session):
    """
    Returns reports based on saved report IDs from the frontend.
    Excludes already saved IDs and handles `is_self` flag.
    """
    saved_report_ids = set(data.saved_report_ids or [])
    is_self = data.is_self

    # Fetch the user
    user = db.query(AuthUser).filter(AuthUser.auth0_id == auth0_user.id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    # Fetch the self-report (NumerologyReportAuth)
    self_report = (
        db.query(NumerologyReportAuth)
        .filter(NumerologyReportAuth.id == user.self_report.id)
        .first()
    )
    if self_report is None:
        raise HTTPException(status_code=404, detail="Self-report not found, Required!")

    # If only self-report is requested
    if is_self:
        self_report_token = create_jwt_token({"report_id": str(self_report.id)})
        return [{
            "report_id": self_report.id,
            "token": self_report_token,
            "user_data": {
                "report_data": self_report.report_data,
                "is_authorized": True,  # Self-report is always authorized
                "is_auth_user": True,
                "instagram": self_report.instagram_username,
                "is_public": self_report.is_public,
                "rating": self_report.rating,
            },
        }]

    # Fetch additional NumerologyReport records
    n_reports_ids = user.n_reports or []  # Ensure it's a list
    # Remove saved_report_ids from n_reports_ids
    filtered_n_reports_ids = [id_ for id_ in n_reports_ids if str(id_) not in saved_report_ids]
    
    additional_reports = []
    if n_reports_ids:
        additional_reports = (
            db.query(NumerologyReport)
            .filter(NumerologyReport.id.in_(filtered_n_reports_ids))  # Query the reduced list
            .all()
        )
    
    
    # print(n_reports_ids, additional_reports)

    # Helper function to process report data
    def process_report_data(report):
        """Process the report and extract report_data."""
        if isinstance(report, NumerologyReport):
            # Fetch sub_report and user details
            sub_report = report.sub_report
            if not sub_report:
                # Fallback: use user details to generate report
                user_data = db.query(User).filter(User.id == report.user_id).first()
                if user_data:
                    person_obj = Person(user_data.dob, user_data.gender, user_data.name)
                    return person_obj.get_all_data()
            else:
                # Parse JSON data and replace name
                try:
                    report_data = sub_report.report_data
                    report_data["person_info"]["name"] = report.person_name
                    return report_data
                except (KeyError, TypeError, json.JSONDecodeError):
                    raise HTTPException(status_code=500, detail="Invalid sub-report data format")
        return None  

    # Initialize response list
    response_list = []

    # Add self-report to the response
    if str(self_report.id) not in saved_report_ids:
        self_report_token = create_jwt_token({"report_id": str(self_report.id)})
        response_list.append({
            "report_id": self_report.id,
            "token": self_report_token,
            "user_data": {
                "report_data": self_report.report_data,
                "is_authorized": True,
                "is_auth_user": True,
                "instagram": self_report.instagram_username,
                "is_public": self_report.is_public,
                "rating": self_report.rating,
            },
        })

    # Add additional reports to the response
    for report in additional_reports:
        token = create_jwt_token({"report_id": str(report.id)})
        response_list.append({
            "report_id": report.id,
            "token": token,
            "user_data": {
                "report_data": process_report_data(report),
                "is_authorized": True, 
                "is_auth_user": False,
                "is_temporary":report.is_temporary,
                "instagram": report.instagram_username,
                "is_public": report.is_public,
                "rating": report.rating,
            },
        })

    return response_list


from fastapi import Query

from sqlalchemy import or_, case
async def search_reports_by_instagram(limit, offset, db: Session, username: str = Query(None)):
    """
    GET /search-reports?username=someusername
    """
    if not username:
        return {"data": []}  # Return empty list if no username is provided

    # Create a case expression to give exact matches priority (1 for exact matches, 2 for partial matches)
    priority = case(
        (NumerologyReport.instagram_username == username, 1),  # Exact match priority = 1
        else_=2  # Partial match priority = 2
    )
    # Fetch reports ordered by the priority (exact matches first, then partial matches)
    reports = db.query(NumerologyReport).filter(
        or_(
            NumerologyReport.instagram_username == username,  # Exact match
            NumerologyReport.instagram_username.like(f"%{username}%")  # Partial match
        )
    ).order_by(priority).offset(offset).limit(limit).all()
    
    # Prepare the result list
    result = [
        {
            "report_id": str(r.id),
            "report_data": {
                "person_info": {
                    **r.sub_report.report_data.get('person_info', {}),
                    "name": r.person_name  # Override the name with r.person_name
                }
            },
            "instagram": r.instagram_username,
            "rating": r.rating,
            "is_public": r.is_public,
            "created_at": r.created_at
        }
        for r in reports
    ]

    return {"data": result}
 
# -------------Update

# REMOVED UPDATING / EDITING AND DELETING ROUTES

# ---------------- ISSUE REPORTING ----------

from .schemas import IssueReportReq

async def report_issue(report_id: UUID, issue_dict:IssueReportReq, db: Session, payload: dict):
    report = db.query(NumerologyReport).filter(NumerologyReport.id == report_id).first()

    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")
    print(issue_dict.description, type(issue_dict))
    issue_description = issue_dict.description
    if not issue_description:
        raise HTTPException(status_code=400, detail="Issue description required")

    # Create a new IssueReport object 
    issue_report = ReportIssues(
        report_id=report_id,
        description=issue_description,
        # status='pending' , # its default
    )
    
    db.add(issue_report)
    db.commit()
    
    return {"message": "Issue reported successfully"}

 