import os
from dotenv import load_dotenv
import smtplib
from email.message import EmailMessage


project_root = os.getcwd()
load_dotenv(os.path.join(project_root, ".env"))

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")


def send_email(email_to: str, name: str):
    print(f"{EMAIL_ADDRESS}, {EMAIL_PASSWORD}")
    # create email
    msg = EmailMessage()
    msg["Subject"] = "Welcome!"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = email_to
    msg.set_content(
        f"Welcome to the library, {name}!\n"
        "Enjoy your adventure in the world of books!"
    )
    # send email
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)
