from fastapi_mail import ConnectionConfig
from insightscapehub.utils import settings

config = ConnectionConfig(
    MAIL_SERVER=settings.EMAIL_HOST,
    MAIL_USERNAME=settings.EMAIL_HOST_USER,
    MAIL_PASSWORD=settings.EMAIL_HOST_PASSWORD,
    MAIL_FROM=settings.EMAIL_FROM,
    MAIL_PORT=settings.EMAIL_PORT,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    MAIL_DEBUG=True,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=True,
    SUPPRESS_SEND=settings.IS_TESTING == True
)
