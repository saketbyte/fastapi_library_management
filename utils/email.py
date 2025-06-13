import smtplib
from email.message import EmailMessage
import os
from dotenv import load_dotenv

load_dotenv()

EMAIL_ADDRESS = "samriddhsingh00@gmail.com"
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")


def send_reminder_email(user_email: str, book_title: str, due_Date: str):
    msg = EmailMessage()
    msg["Subject"] = "Book Reminder"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = user_email
    msg.set_content(
        "Demo mail"
    )

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
    except Exception as e:
        print(e)