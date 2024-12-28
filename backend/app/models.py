#models.py
# from datetime import datetime, timezone
from .database import Base, DATABASE_URL
from geoalchemy2 import Geography
from sqlalchemy import  Column, Table, DateTime, Integer, String, Boolean, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid 

# Choose the correct JSON type based on the database
if "postgresql" in DATABASE_URL:
    JSON_TYPE = JSONB  # Use JSONB for PostgreSQL
else:
    JSON_TYPE = JSON  # Use JSON (text) for SQLite (DEVELOPMENT)
    
# -----------------Authorization------------------



# Many-to-Many relationship for friends
friend_association = Table(
    'friend_association', Base.metadata,
    Column('user_id', UUID(as_uuid=True), ForeignKey('auth_users.id'), primary_key=True),
    Column('friend_id', UUID(as_uuid=True), ForeignKey('auth_users.id'), primary_key=True)
)


""" Though auth0 will manage login/singup , its a subscription class that user gets for further service """
class AuthUser(Base):
    __tablename__ = "auth_users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    auth0_id = Column(String, unique=True, nullable=False)  # Auth0 user ID
    email = Column(String, nullable=False)
    fullname = Column(String)
    dob = Column(String(10))
    gender = Column(String(8))
    picture = Column(String, nullable=True) # if its null means this user is delete, (behaving it like is_deleted)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    n_reports = Column(JSON, nullable=True) # only NumerologyReport reports in this
    self_report = relationship("NumerologyReportAuth", back_populates="auth_user", uselist=False, lazy="select", cascade="all, delete, delete-orphan")

    address = Column(JSON_TYPE, nullable=True)  # Human-readable address
    location = Column(Geography(geometry_type='POINT', srid=4326), nullable=True)
   
    friends = relationship(
        "AuthUser",
        secondary=friend_association,
        primaryjoin=id == friend_association.c.user_id,
        secondaryjoin=id == friend_association.c.friend_id,
        lazy="select"
    )
    
class FriendRequest(Base):
    __tablename__ = "friend_requests"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    sender_id = Column(UUID(as_uuid=True), ForeignKey('auth_users.id'))
    receiver_id = Column(UUID(as_uuid=True), ForeignKey('auth_users.id'))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    sender = relationship("AuthUser", foreign_keys=[sender_id])
    receiver = relationship("AuthUser", foreign_keys=[receiver_id])


class NumerologyReportAuth(Base):
    """ This reports is personal to authuser (self reports), and more personalized... """
    __tablename__ = "numerology_reports_auth"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('auth_users.id'), nullable=False)
    is_public = Column(Boolean, default=True)
    instagram_username = Column(String(20), nullable=True) 
    rating = Column(Integer, default=3) 
    report_data = Column(JSON_TYPE, nullable=False)
    summary = Column(String(800), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now()) #same as authuser creation
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Reverse relationship
    auth_user = relationship("AuthUser", back_populates="self_report")
 

# ------------------- FOR PUBLIC/GUEST USERS ------------------------ optimized!!!  

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(30), index=True)
    dob = Column(String(10))
    gender = Column(String(8))

    
class NumerologyReport(Base):
    __tablename__ = "numerology_reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    person_name = Column(String(30), nullable=True)  # store person's name (as sub_report_id might have another name, so to replace it from this or user_id.name)
    
    sub_report_id = Column(UUID(as_uuid=True), ForeignKey('sub_reports.id'),index=True)  # Reference to SubReport
    is_public = Column(Boolean, default=True)
    instagram_username = Column(String(16), nullable=True)
    rating = Column(Integer, default=3)
    created_at = Column(DateTime(timezone=True), server_default=func.now(),nullable=True)

    is_temporary = Column(Boolean, default=True)
    # Relationship to SubReport
    sub_report = relationship("SubReport", backref="reports")
    
     
class SubReport(Base):
    __tablename__ = "sub_reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    report_data = Column(JSON_TYPE) 
    
    # this is for fast lookup, to use same report for common bithdate, (hard to query from orm in above report_data(json) )
    dob = Column(String,nullable=True, index=True)  
    gender = Column(String,nullable=True, index=True)

# --------------- MATCHING ---------

class CompatibilityReport(Base):
    __tablename__ = "compatibility_reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user1_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user2_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    person1_name = Column(String(25))  # store person's name (as sub_match_id's data might have another name, so to replace it from that)
    person2_name = Column(String(25))
    
    sub_match_id = Column(UUID(as_uuid=True), ForeignKey('sub_matches.id'),index=True)  # Reference to SubMatch
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship to SubReport
    sub_match = relationship("SubMatch", backref="matches")
    
class SubMatch(Base):
    __tablename__ = "sub_matches"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    match_data = Column(JSON_TYPE)
    
    dob1 = Column(String,nullable=True, index=True)  
    gender1 = Column(String,nullable=True, index=True)
    
    dob2 = Column(String,nullable=True, index=True)  
    gender2 = Column(String,nullable=True, index=True)
    


class EmailSubscription(Base):
    __tablename__ = "email_subscriptions"

    email = Column(String, primary_key=True, unique=True, index=True)
    # report_id = Column(UUID(as_uuid=True), ForeignKey('numerology_reports.id'))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    


class ReportIssues(Base):
    __tablename__ = 'report_issues'
    
    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(UUID(as_uuid=True), ForeignKey('numerology_reports.id'))
    description = Column(String )
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String, default='pending')
    