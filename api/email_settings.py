import os
from dotenv import load_dotenv
from fastapi_mail import FastMail, MessageSchema, MessageType, ConnectionConfig


project_root = os.getcwd()
load_dotenv(os.path.join(project_root, ".env"))


class Envs:
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_FROM = os.getenv("MAIL_FROM")
    MAIL_PORT = int(os.getenv("MAIL_PORT"))
    MAIL_SERVER = os.getenv("MAIL_SERVER")


conf = ConnectionConfig(
    MAIL_USERNAME=Envs.MAIL_USERNAME,
    MAIL_PASSWORD=Envs.MAIL_PASSWORD,
    MAIL_FROM=Envs.MAIL_FROM,
    MAIL_PORT=Envs.MAIL_PORT,
    MAIL_SERVER=Envs.MAIL_SERVER,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    TEMPLATE_FOLDER=os.path.join(project_root, "api/templates/email")
)


async def send_welcome_email(email_to: str, body: dict):
    # create email
    message = MessageSchema(
        subject="Welcome!",
        recipients=[email_to],
        template_body=body,
        subtype=MessageType.html,
    )

    fm = FastMail(conf)
    await fm.send_message(message, template_name="welcome.html")
