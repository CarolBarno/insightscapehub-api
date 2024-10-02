from fastapi_mail import MessageSchema, MessageType
from app.mail_config import get_mailer_instance
from insightscapehub.models.user import User, Status
from insightscapehub.models.verification import VerificationToken


async def send_email(subject: str, recipient: str, template: str, template_body: dict):
    mailer = get_mailer_instance()
    message = MessageSchema(
        subject=subject,
        recipients=[recipient],
        subtype=MessageType.html,
        template_body=template_body
    )
    await mailer.send_message(message, template)


async def send_reg_email(user: User, token: VerificationToken):
    if not user or user.status != Status.PENDING.value:
        return

    template_body = {
        'recipient': user.email,
        'verification_link': token.auth_link
    }
    await send_email(
        subject='Account created',
        recipient=user.email,
        template='account_verification.html',
        template_body=template_body
    )


async def send_reset_password(token: VerificationToken):
    if not token or not token.user or not token.host:
        return

    user: User = token.user

    template_body = {
        'recipient': user.email,
        'reset_link': token.auth_link
    }
    await send_email(
        subject='Password Reset',
        recipient=user.email,
        template='password_reset.html',
        template_body=template_body
    )
