import os

from fastapi_mail import FastMail, MessageSchema, MessageType

from smtp.config import MAIL_BCC, MAIL_REDIRECT_TO, EUREKA_EMAIL_SIGNATURE, CONNECTION_CONFIG

def send_email(subject, recipients, body, attachments, background_tasks):
    message = MessageSchema(
        subject=subject,
        recipients=[MAIL_REDIRECT_TO or recipients],
        bcc=MAIL_BCC,
        body=body+EUREKA_EMAIL_SIGNATURE,
        subtype=MessageType.html,
        attachments=attachments
    )

    # 4. Send (Background Task to avoid blocking UI)
    fm = FastMail(CONNECTION_CONFIG)
    background_tasks.add_task(fm.send_message, message)
    