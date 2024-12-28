#schemas.py

from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, field_validator


from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
from .models import AuthUser

# ------------------ AUTHORIZATION-------------

# for all location based request,
class LocationRequest(BaseModel):
    source: Optional[str] = Field(None, max_length=12)
    lon: float = Field(..., ge=-180, le=180)
    lat: float = Field(..., ge=-90, le=90)
    name: Optional[str] = Field(None, max_length=60)
    county: Optional[str] = Field(None, max_length=30)
    state: Optional[str] = Field(None, max_length=30)
    district: Optional[str] = Field(None, max_length=30)
    postcode: Optional[str] = Field(None, max_length=15)
    country: Optional[str] = Field(None, max_length=30)
    country_code: Optional[str] = Field(None, max_length=2)
    city: Optional[str] = Field(None, max_length=20)
    neighbourhood: Optional[str] = Field(None, max_length=20)
    suburb: Optional[str] = Field(None, max_length=20)
  
    class Config:
        from_attributes = True
        exclude_none = True
    
    def clean_dump(self):
        """Removes keys with None or empty string values."""
        return {key: value for key, value in self.model_dump(exclude_none=True).items() if value not in [None, ""]}
 

from datetime import datetime

# Helper function to validate the Date of Birth
def validate_dob(dob: str):
    try:
        date_obj = datetime.strptime(dob, "%Y-%m-%d")  
        current_year = datetime.now().year
        if not (1900 <= date_obj.year <= current_year):
            raise ValueError(f"Year must be between 1900 and {current_year}.")
    except ValueError as e:
        raise ValueError(f"Invalid dob: {dob}. Error: {str(e)}")
    
class AuthUserCreate(BaseModel):
    auth0_id: str = Field(..., description="Unique Auth0 user identifier")
    email: EmailStr
    fullname: str = Field(..., min_length=1, max_length=30)
    dob: str = Field(..., min_length=6, max_length=10)
    gender: str = Field(..., min_length=1, max_length=7)
    picture: Optional[str] = None
    address: Optional[LocationRequest] = None
    
    @field_validator('dob')
    def validate_dob_field(cls, v):
        validate_dob(v)
        return v


class AuthUserResponse(BaseModel):
    # id: UUID
    # auth0_id: str
    email: EmailStr
    fullname: str
    dob: str
    gender: str
    picture: Optional[str] = None
    self_report_id: Optional[UUID] = None
    created_at: datetime  
    # n_reports: Optional[List[dict]] = None  
    
    @classmethod
    def from_orm(cls, user: AuthUser):
        """Custom ORM mapping to include `self_report_id` from the relationship."""
        return cls(
            email=user.email,
            fullname=user.fullname,
            dob=user.dob,
            gender=user.gender,
            picture=user.picture,
            self_report_id=user.self_report.id if user.self_report else None,
            created_at=user.created_at,
        )


    class Config:
        from_attributes = True

# class AuthUserResponseBasic(BaseModel):
#     # id: UUID
#     # email: EmailStr
#     fullname: str
#     dob: str
#     gender: str
#     # picture: Optional[str] = None
#     # self_report_id: Optional[str] = None

#     class Config: 
#         from_attributes = True


class FriendRequestSchema(BaseModel):
    receiver_id: UUID
    class Config:
        from_attributes = True
     
       
class UpdateProfile(BaseModel):
    picture: str
    class Config:
        from_attributes = True
 


# ------------PUBLIC--------------


class PersonData(BaseModel):
    name: str = Field(..., min_length=1, max_length=30) 
    dob: str  
    gender: str = Field(..., min_length=3, max_length=6) 

class CompatibilityMatchRequest(BaseModel):
    person_1: PersonData
    person_2: PersonData

class ReportOut(BaseModel):
    report_id: int
    report_data: str
    
class ReportCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=30) 
    dob: str = Field(..., min_length=6, max_length=12)
    gender: str = Field(..., min_length=3, max_length=6)
    auth0_id: Optional[str] = None
    
    class Config:
        from_attributes = True
    
class SocialLinks(BaseModel):
    instagram: str = Field(..., min_length=1, max_length=15)
    class Config:
        from_attributes = True 

class ReportRating(BaseModel):
    rating: int
    class Config:
        from_attributes = True
    
class ReportVisibility(BaseModel):
    public: bool
    class Config:
        from_attributes = True
 
class SavedReportIDs(BaseModel):
    saved_report_ids: Optional[List[str]] = None  
    is_self: Optional[bool] = False

class EmailRequest(BaseModel):
    email: EmailStr
    class Config:
        from_attributes = True


class EditReportRequest(BaseModel):
    is_public: bool = Field(..., description="Set the report visibility")
    name: Optional[str] = Field(None, description="User Fullname")
    instagram: Optional[str] = Field(None, description="Instagram username")
    rating: Optional[int] = Field(None, ge=3, le=5, description="Rating between 3 and 5")
    class Config:
        from_attributes = True
    
    
class IssueReportReq(BaseModel):
    description: str = Field(..., min_length=1, max_length=400) 
    class Config:
        from_attributes = True


class GetProfilePic(BaseModel):
    id: Optional[str] = None