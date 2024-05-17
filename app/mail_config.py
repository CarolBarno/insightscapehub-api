from pathlib import Path
from fastapi_mail import ConnectionConfig, FastMail

here = Path(__file__).parent.joinpath('templates').resolve()


def get_mailer_instance() -> FastMail:
    from insightscapehub.utils.mailer import config

    config: ConnectionConfig = config.model_copy(
        update={
            'TEMPLATE_FOLDER': here,
            'MAIL_FROM': config.MAIL_FROM,
            'MAIL_SSL_TLS': False,
            'MAIL_STARTTLS': False
        }
    )

    mailer = FastMail(config)

    return mailer
