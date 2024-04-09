from pathlib import Path

from fastapi_mail import ConnectionConfig
from fastapi_mail import FastMail
from fastapi_mail import MessageSchema
from fastapi_mail import MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr

from src.database.config import config
from src.services.auth import auth_service

conf = ConnectionConfig(
    MAIL_USERNAME=config.MAIL_USERNAME,
    MAIL_PASSWORD=config.MAIL_PASSWORD,
    MAIL_FROM=config.MAIL_FROM,
    MAIL_PORT=config.MAIL_PORT,
    MAIL_SERVER=config.MAIL_SERVER,
    MAIL_FROM_NAME=config.MAIL_FROM_NAME,
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent / "templates",
)


async def send_email(email: EmailStr, username: str, host: str):
    """
    The send_email function sends an email to the user with a link to confirm their email address.
        The function takes in three parameters:
            -email: the user's email address, which is used as a unique identifier for each account.
            -username: the username of the account that was just created. This is included in case
                there are multiple accounts associated with one email address (e.g., if someone has
                both a personal and work account). It helps users identify which account they're confirming.

    :param email: EmailStr: Specify the email address of the user
    :param username: str: Send the username to the email template
    :param host: str: Pass in the host name of the server
    :return: A coroutine object
    :doc-author: Trelent
    """
    try:
        token_verification = auth_service.create_email_token({"sub": email})
        message = MessageSchema(
            subject="Confirm your email ",
            recipients=[email],
            template_body={
                "host": host,
                "username": username,
                "token": token_verification,
            },
            subtype=MessageType.html,
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="email_template.html")
    except ConnectionErrors as err:
        print(err)
