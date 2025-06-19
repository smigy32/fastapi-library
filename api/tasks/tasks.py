from celery import Celery
from fastapi_mail import FastMail, MessageSchema, MessageType
from fpdf import FPDF
from asgiref.sync import async_to_sync

from api.email_settings import conf

celery_app = Celery("tasks")


@celery_app.task
def generate_pdf(items: list, type: str):
    pdf = FPDF()
    pdf.set_font("helvetica", size=16)
    for item in items:
        if type == "books":
            pdf.add_page()
            pdf.set_font(size=24, style="B")
            pdf.cell(text=f"{item['title']}", ln=True)
            pdf.set_font(size=16, style="I")
            pdf.cell(text="Description:", ln=True)
            pdf.set_font(style="")
            pdf.multi_cell(text=f"{item['description']}", w=0)
    pdf.output("attachments/catalog.pdf")


@celery_app.task
def send_welcome_email(email_to: str, body: dict):
    # create email
    message = MessageSchema(
        subject="Welcome!",
        recipients=[email_to],
        template_body=body,
        subtype=MessageType.html,
    )

    fm = FastMail(conf)
    send_message_sync = async_to_sync(fm.send_message)  # wrap the asynchronous call
    send_message_sync(message, template_name="welcome.html")
