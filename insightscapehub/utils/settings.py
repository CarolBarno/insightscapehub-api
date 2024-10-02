import os
from dotenv import load_dotenv
from typing import Union
from insightscapehub.utils.enums import AppsEnum
from pathlib import Path

load_dotenv()

# SECURITY
DEBUG = os.environ.get("DEBUG", False)
IS_TESTING = os.environ.get("IS_TESTING", False)

SECRET_KEY = os.environ.get(
    "SECRET_KEY", "355206193b79659a5397bb0e6f043711954c00ed5fa52f08d9e615f8ff1d9fcc")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# DATABASE CONFIGS
DB_USER = os.environ.get("DB_USER", "postgres")
DB_NAME = os.environ.get("DB_NAME", "flip_v2")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "admin")
DB_HOST = os.environ.get("DB_HOST", "0.0.0.0")
DB_PORT = os.environ.get("DB_PORT", "5432")

DB_URL = os.environ.get(
    "DB_URL", f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

# APP CONFIGS
APP_PREFIX: Union[str, None] = None

# Internals
APP_NAME: Union[AppsEnum, None] = None
APP_HOME: Union[Path, None] = None
if not APP_HOME:
    APP_HOME = Path(os.getcwd())

REQUEST_LIMIT = os.environ.get('REQUEST_LIMIT', 100)
REQUEST_INTERVAL = os.environ.get('REQUEST_INTERVAL', 60)
APP_PORT = os.environ.get('PORT', 5501)

# MAIL CONFIGURATIONS
EMAIL_HOST = os.environ.get('EMAIL_HOST', None)
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', None)
EMAIL_FROM = os.environ.get('EMAIL_FROM', EMAIL_HOST_USER)
MAIL_FROM_NAME = os.environ.get('EMAIL_FROM_NAME', None)
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', None)
EMAIL_PORT = os.environ.get('EMAIL_PORT', None)
EMAIL_USE_SSL = False
