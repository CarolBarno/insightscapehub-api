from app.views import (auth_router, password_router, verify_router)
import pathlib
from insightscapehub.utils.enums import AppsEnum, AppPrefixes
from insightscapehub.utils.create_app import App
from insightscapehub import models
from insightscapehub.utils.db import engine

BASE_PATH = pathlib.Path(pathlib.Path(__file__).parent.parent)
models.Base.metadata.create_all(bind=engine)

routers = (auth_router, password_router, verify_router)

instance = App(
    AppsEnum.BASE,
    routers,
    APP_HOME=BASE_PATH,
    prefix=AppPrefixes.BASE.value
)

app = instance.configure()
