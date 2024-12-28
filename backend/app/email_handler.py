#email_handler.py
 
from sqlalchemy.orm import Session
from fastapi import HTTPException
from .models import EmailSubscription
from backend.utils.Numerology import Person

async def handle_email_subscription(email: str, db: Session):
    if db.query(EmailSubscription).filter(EmailSubscription.email == email).first():
        raise HTTPException(status_code=409, detail="Email already subscribed!")
    
    subscription = EmailSubscription(email=email)
    db.add(subscription)
    db.commit() 
    return {"message": "Subscribed!"}

async def handle_email_sending(user_data: dict, email: str):
    person_obj = Person(user_data.get('dob'), user_data.get('gender'), user_data.get('name'))
    report_content = person_obj.to_str()
    await send_email(email, report_content)


import asyncio
# import aiosmtplib
import smtplib
from email.mime.text import MIMEText 
from .config import SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, FROM_EMAIL

async def send_email(email: str, report_content: str):    
    msg = MIMEText(report_content)
    msg["Subject"] = "Your Numerology Report"
    msg["From"] = FROM_EMAIL
    msg["To"] = email

    try:
        # Use asyncio.to_thread to run the blocking code
        await asyncio.to_thread(send_email_sync, msg, email)
        # Use aiosmtplib to send the email asynchronously
        # await aiosmtplib.send(
        #     msg,
        #     hostname=SMTP_SERVER,
        #     port=SMTP_PORT,
        #     username=SMTP_USERNAME,
        #     password=SMTP_PASSWORD,
        #     start_tls=True
        # )
    except Exception as e:
        print(f"Failed to send email. {e}")
        # Optionally, raise an HTTPException or handle it as needed
    print("SEND to @ ",email)

def send_email_sync(msg, email):
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(FROM_EMAIL, [email], msg.as_string())

 
# async def send_email(email: str, report_content: str):
#     from .config import SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, FROM_EMAIL
    
#     import smtplib
#     from email.mime.text import MIMEText
 
#     msg = MIMEText(report_content)
#     msg["Subject"] = "Your Numerology Report"
#     msg["From"] = FROM_EMAIL
#     msg["To"] = email

#     try:
#         async with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
#             await server.starttls()
#             await server.login(SMTP_USERNAME, SMTP_PASSWORD)
#             await server.sendmail(FROM_EMAIL, [email], msg.as_string())
#     except Exception as e:
#         print(f"Failed to send email. {e}")
#         # raise HTTPException(status_code=500, detail="Failed to send email.")
