from fastapi import UploadFile
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from groundible_admin.root.settings import Settings
from typing import List
from pathlib import Path
import logging


settings = Settings()

LOGGER = logging.getLogger(__name__)

conf = ConnectionConfig(
    MAIL_USERNAME=settings.mail_username,
    MAIL_PASSWORD=settings.mail_password,
    MAIL_FROM=settings.mail_from,
    MAIL_PORT=settings.mail_port,
    MAIL_SERVER=settings.mail_server,
    MAIL_FROM_NAME=settings.mail_from_name,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent.parent / "templates/",
)


async def send_mail(
    subject: str,
    reciepients: List[str],
    payload: dict,
    template: str,
    attachments: List[UploadFile] = [],
):
    message = MessageSchema(
        subject=subject,
        recipients=reciepients,
        subtype=MessageType.html,
        attachments=attachments,
        template_body=payload,
    )

    fm = FastMail(conf)

    try:
        # send mail
        await fm.send_message(message, template_name=template)

    except ConnectionErrors as e:
        LOGGER.exception(e)
        LOGGER.error(f"mail failed to send for {payload}, with subject: {subject}")
        pass
