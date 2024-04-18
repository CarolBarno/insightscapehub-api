from app.views import (auth_router)
import pathlib
from insightscapehub.utils.enums import AppsEnum, AppPrefixes
from insightscapehub.utils.create_app import App

BASE_PATH = pathlib.Path(pathlib.Path(__file__).parent.parent)

routers = (auth_router)

instance = App(
    AppsEnum.BASE,
    routers,
    APP_HOME=BASE_PATH,
    prefix=AppPrefixes.BASE.value
)

app = instance.configure()
