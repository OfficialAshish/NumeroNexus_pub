
# a_routes.py
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import JSONResponse

from .limiter import limiter
from .schemas import LocationRequest ,AuthUserCreate , UpdateProfile, AuthUser
from sqlalchemy.orm import Session
from sqlalchemy import func
from .database import get_db
from .authorization import auth0_user_dependency
from .jwt import create_jwt_token
from .config import GEO_API_KEY
from fastapi import status
from fastapi_auth0 import Auth0User
from .models import AuthUser , NumerologyReportAuth
from backend.utils.Numerology import Person


router = APIRouter()
 
# Authenticated routes....................

# HAVE TO REMOVE SOME ROUTES FOR SECURITY REASONS
  

# depreciated 
# @router.get("/user/basic")
# @limiter.limit("8/minute")
# async def get_auth_user_basic(request: Request, auth0_user: Auth0User = Depends(auth0_user_dependency), db: Session = Depends(get_db)):
#     """ If AuthUser, then send its basic details for frontend to match compatibility mainly """
#     # print(vars(auth0_user))
#     user = db.query(AuthUser).filter(AuthUser.auth0_id == auth0_user.id).first()
#     if not user:
#         raise HTTPException(status_code=404, detail="Subscription Required!")
    
#     return {
#         "fullname": user.fullname,
#         "dob": user.dob, 
#         "gender": user.gender,
#         "self_report_id": user.self_report.id if user.self_report else None,
#         "created_at": user.created_at
#     }


# depreciated,(in subscription itself profileData gets save all once)
# @router.get("/valid_user")
# @limiter.limit("5/minute")
# async def check_auth_user(request: Request, auth0_user: Auth0User = Depends(auth0_user_dependency), db: Session = Depends(get_db)):
#     """ Validates if user is subscribed. """
#     # print(vars(auth0_user))
#     user = db.query(AuthUser).filter(AuthUser.auth0_id == auth0_user.id).first()
#     if not user:
#         raise HTTPException(status_code=404, detail="Subscription Required!")
#     return {"user_id":user.id}


@router.put("/edit/profile")
@limiter.limit("6/minute")
async def update_profile(request: Request, userdata : UpdateProfile, auth0_user: Auth0User = Depends(auth0_user_dependency), db: Session = Depends(get_db)):
    """ Updates profile picture. """
    # print(vars(auth0_user))
    # print(userdata)
    user = db.query(AuthUser).filter(AuthUser.auth0_id == auth0_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User Not Found.")
    user.picture = userdata.picture
    db.commit()
    return {"picture" : user.picture}
 

@router.put("/edit/location")
@limiter.limit("3/minute")
async def update_location(
    request: Request,
    location_data: LocationRequest,  # The input data (lat, lon, address)
    auth0_user: Auth0User = Depends(auth0_user_dependency),  
    db: Session = Depends(get_db) 
):
    """ Updates address and location for the user. """
    # print(location_data)
    # Retrieve the user based on Auth0 ID
    user = db.query(AuthUser).filter(AuthUser.auth0_id == auth0_user.id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User Not Found.")
    
    try:
        # Create Geography point for latitude and longitude
        lat = location_data.lat
        lon = location_data.lon
        # Create the WKT string for the point (lon, lat)
        point_wkt = f"POINT({lon} { lat})"
        
        # Use ST_GeogFromText to convert the WKT string to a geography object
        user.location = func.ST_GeogFromText(point_wkt)
    
        # print(location_data.clean_dump())
        
        user.address = location_data.clean_dump()  # Only includes provided fields

        db.commit()

    except Exception as e:
        db.rollback()
        print(e)
        raise HTTPException(status_code=500, detail=f"Failed to save location: {str(e)}")
     
    return {"message": "Location updated successfully", "address": user.address}


# to authenticate the all reports and return thier new tokens for each,


from .controllers import get_report_setAuth
from .schemas import SavedReportIDs

@router.post("/setrep")
@limiter.limit("5/minute")
async def get_token_report(
    request: Request,
    data: SavedReportIDs, 
    auth0_user: Auth0User = Depends(auth0_user_dependency),  
    db: Session = Depends(get_db) 
):
    return await get_report_setAuth(auth0_user,data, db)
 