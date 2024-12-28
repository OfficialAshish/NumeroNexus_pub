#routes.py

from datetime import timezone
from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends, Query, Request

from .schemas import *

from sqlalchemy.orm import Session
from .database import get_db

from .authorization import JWTBearer

from .limiter import limiter
from .controllers import *

router = APIRouter()

@router.post("/profile")
@limiter.limit("6/minute")
async def get_picture(request: Request ,user_d: GetProfilePic , db: Session = Depends(get_db)):
    try:
        # print(vars(user_d))
        existing_user = db.query(AuthUser).filter(AuthUser.auth0_id == user_d.id).first()
        if existing_user is None:
            return {"picture":''} 
        return {"picture":existing_user.picture}           
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation failed: {e}")
 
@router.post("/report")
@limiter.limit("6/minute")
async def create_report(request: Request ,report: ReportCreate, db: Session = Depends(get_db)):
    try:
        return await generate_report(report, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation failed: {e}")
 
# DEPRECIATED
# @router.get("/reports")
# @limiter.limit("10/minute")
# async def read_public_reports(request:Request, limit: int = Query(10, ge=1), offset: int = Query(0, ge=0), db: Session = Depends(get_db)):
#     return await get_public_reports(db, limit, offset)


# For search using instagram username
@router.get("/search-reports")
@limiter.limit("10/minute")
async def read_search_reports(
    request:Request, 
    username: str = Query(None),
    limit: int = Query(15, ge=0, le=20),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    return await search_reports_by_instagram( limit, offset, db, username)


@router.get("/r/{report_id}")
@limiter.limit("8/minute")
async def get_by_uuid(
    request:Request, report_id: UUID, 
    db: Session = Depends(get_db), 
    payload: dict = Depends(JWTBearer())
    ):
    return await get_report(report_id, db, payload)


# @router.get("/gen-summary/{report_id}")
# @limiter.limit("3/day")
# async def gen_summary(
#     request:Request, report_id: UUID, 
#     db: Session = Depends(get_db), 
#     payload: dict = Depends(JWTBearer())
# ):
#     return await generate_summary(report_id, db, payload)

@router.get("/rem-summary/{report_id}", status_code=200)
@limiter.limit("5/minute")
async def rem_summary(
    request:Request, report_id: UUID, 
    db: Session = Depends(get_db), 
    payload: dict = Depends(JWTBearer())
):
    try:
        # Fetch the report by ID
        report = db.query(NumerologyReportAuth).filter(NumerologyReportAuth.id == report_id).first()
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")

        # Validate user permissions
        if not payload or str(report.id) != payload.get('report_id'):
            raise HTTPException(status_code=403, detail="Permission denied")

        report.summary = None
        report.updated_at = datetime.now(timezone.utc)
        db.commit()
        return {"status": "success" }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")




@router.put("/r/{report_id}/visibility")
@limiter.limit("4/minute")  # Limit this endpoint to 5 requests per minute
async def make_public(
    request: Request,  
    report_id: UUID, 
    visibility: ReportVisibility, 
    db: Session = Depends(get_db), 
    payload: dict = Depends(JWTBearer())
):
    return await update_report_visibility(report_id, db, visibility.is_public, payload)

@router.put("/r/{report_id}/social-links")
@limiter.limit("6/minute")
async def add_links(
    request: Request,  
    report_id: UUID, 
    links: SocialLinks, 
    db: Session = Depends(get_db), 
    payload: dict = Depends(JWTBearer())
):
    return await update_social_links(report_id, db, links.instagram, payload)

@router.put("/r/{report_id}/rate")
@limiter.limit("4/minute")
async def rate(
    request: Request,  
    report_id: UUID, 
    rating: ReportRating, 
    db: Session = Depends(get_db), 
    payload: dict = Depends(JWTBearer())
):
    return await rate_report(report_id, rating.rating, db, payload)


@router.put("/r/{report_id}/edit")
@limiter.limit("6/minute")
async def update_report(
    request: Request,  
    report_id: UUID, 
    edit_req: EditReportRequest, 
    db: Session = Depends(get_db), 
    payload: dict = Depends(JWTBearer())
):
    return await edit_report(report_id, edit_req, db, payload)
 
 
# ---------- remove and report-----------

from .controllers import remove_report, report_issue

@router.delete("/del/{report_id}")
@limiter.limit("4/minute")
async def delete_report(
    request: Request,  
    report_id: UUID, 
    db: Session = Depends(get_db), 
    payload: dict = Depends(JWTBearer())
): 
    return await remove_report(report_id, db, payload)

@router.post("/issue/{report_id}")
@limiter.limit("3/minute")
async def issue_report(
    request: Request,  
    report_id: UUID, 
    issue_data:IssueReportReq,
    db: Session = Depends(get_db), 
    payload: dict = Depends(JWTBearer())
):
    return await report_issue(report_id, issue_data, db, payload)


# ----------------------- MATCHING COMPATIBILITY-------------

 
@router.delete("/del_match/{match_id}")
@limiter.limit("6/minute")
async def delete_compatibility_report(
    request: Request,
    match_id: UUID, 
    db: Session = Depends(get_db)
): 
    return await remove_match(match_id, db)

@router.post("/match")
@limiter.limit("6/minute")
async def create_compatibility_report(request: Request,
        match_request: CompatibilityMatchRequest, 
        db: Session = Depends(get_db)
    ):
    return await generate_compatibility_report(match_request, db)
    
    
@router.get("/m/{match_id}")
@limiter.limit("6/minute")
async def get_match_uuid(
    request:Request, match_id: UUID, 
    db: Session = Depends(get_db)
    ):
    return await get_match(match_id, db)


# --------------------  EMAIL RELATED ------------

from .email_handler import *
from fastapi import BackgroundTasks
from .models import User, NumerologyReport

@router.post("/email/{report_id}")
@limiter.limit("4/minute")
async def email_send(
    request :Request,
    report_id: UUID, eml_req: EmailRequest, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    payload: dict = Depends(JWTBearer())
):
    # Validate report existence and permission before adding the background task
    raise HTTPException(status_code=400, detail="Implementation Moved!.")

    report = db.query(NumerologyReport).filter(NumerologyReport.id == report_id).first()
    if report is None:
        report = db.query(NumerologyReportAuth).filter(NumerologyReportAuth.id == report_id).first()

    if report is None:
        raise HTTPException(status_code=404, detail=f"Report with ID {report_id} not found.")
    
    if not payload or str(report.id) != payload.get('report_id'):
        raise HTTPException(status_code=403, detail="Permission denied. Not your report.")

    user = db.query(User).filter(User.id == report.user_id).first()
    # print(report, report.user_id, user)
    if user:
        subscription = EmailSubscription(report_id = report_id, email = eml_req.email)
        db.add(subscription)
        db.commit()
        user_data = {'name':user.name, 'dob':user.dob, 'gender':user.gender}
        background_tasks.add_task(handle_email_sending, user_data, eml_req.email)
        return {"message": "Email sending task has been initiated."}
        # Call the async email sending function directly
        # await handle_email_sending(user_data, eml_req.email)
        # return {"message": "Email has been sent."}
        
    return {"message": "Let see you again."}
    
@router.post("/email")
@limiter.limit("5/minute")
async def email_subscribe(request:Request, eml_req: EmailRequest, db: Session = Depends(get_db) ):
    return await handle_email_subscription(eml_req.email , db)
  
  



# ------------------testing--------------
from typing import List 
    
@router.post("/bulk-rpt")
@limiter.limit("5/minute")
async def create_bulk_report(request: Request, reports: List[ReportCreate], db: Session = Depends(get_db)):
    try:
        results = []
        # print(reports)
        
        for report in reports[:20]:
            report_result = await generate_report(report, db)
            results.append(report_result)
        
        # Save the results to a JSON file
        with open("bulk_report_results.json", "w+") as f:
            # json.dump(results, f)
            json.dump(results, f, default=str)  


        return {
            "message": "Bulk reports generated successfully.",
            "results_file": "bulk_report_results.json"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bulk report generation failed: {e}")
    
import random
# Mock function to generate random Instagram usernames
def generate_random_username():
    usernames = [
        "user123", "cool_guy", "fashionista99", "foodlover", "travel_enthusiast",
        "fitness_junkie", "artistic_soul", "tech_guru", "nature_lover", "bookworm"
    ]
    return random.choice(usernames)


                           
@router.post("/bulk-ic")
@limiter.limit("3/minute")
async def make_reports_public(request: Request, db: Session = Depends(get_db)):
    try:
        # Load the previously generated reports from JSON file
        with open("bulk_report_results.json", "r") as f:
            results = json.load(f)

        # Iterate through the results to update visibility and social links
        for result in results:
            report_id = result["report_id"]
            report = db.query(NumerologyReport).filter(NumerologyReport.id == UUID(report_id)).first()
            
            if report is None:
                print(f"Report with ID {report_id} not found.")
                continue
            
            # Make report public and assign a random Instagram username
            report.is_public = True
            report.instagram_username = generate_random_username()
            db.commit()

        return {"message": "All reports updated to public with random social links."}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating reports: {str(e)}")
    
    
    
    # -------------------!!!!!!!!!!!!--------------!!!!!!!!!!!!!!-----------!!!!!!!!!!!!!!!!


# from .a_routes import router as auth_router  
