import pathlib
from typing import List, Optional, Tuple, Union
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from insightscapehub.utils.rate_limiter import RateLimitMiddleware
from insightscapehub.utils import settings
from insightscapehub.utils.docs import docs_router


class App:

    def __init__(self, service_name: str, routers: Tuple[APIRouter] = [], APP_HOME=None, description: Optional[str] = None, prefix: Optional[Union[str, None]] = None) -> None:
        self.service_name = service_name
        self.routers = self._initialize_routers([routers]) if routers else []
        self.description = (
            description if description else 'InsightScape Microservice for %s' % service_name)

        settings.APP_PREFIX = self.prefix = prefix
        self.set_app_home(APP_HOME)

    def configure(self):
        app = FastAPI(debug=settings.DEBUG, docs_url=None, title=self.service_name,
                      description=self.description, openapi_url=self.prefix + '/openapi.json' if self.prefix else None)

        origins = ['*']

        app.add_middleware(CORSMiddleware, allow_origins=origins,
                           allow_credentials=True, allow_methods=['*'], allow_headers=['*'])

        app.add_middleware(
            RateLimitMiddleware, limit=settings.REQUEST_LIMIT, interval=settings.REQUEST_INTERVAL)

        base_router = APIRouter(prefix=self.prefix) if self.prefix else app

        settings.APP_NAME = self.service_name

        for router in self.routers:
            base_router.include_router(router)

        base_router.include_router(docs_router)

        if self.prefix:
            app.include_router(base_router)

        return app

    def set_app_home(self, APP_HOME: pathlib.Path):
        if not APP_HOME and not settings.APP_HOME:
            raise ValueError('Please set the APP_HOME value.')
        elif not settings.APP_HOME:
            if not isinstance(APP_HOME, pathlib.Path):
                raise ValueError(
                    f'APP_HOME must be an instance of pathlib.Path')

            settings.APP_HOME = APP_HOME
        else:
            print('APP_HOME is already set to', settings.APP_HOME)

    def _initialize_routers(self, routers: List[APIRouter]):
        try:
            from insightscapehub.decorators import initialize_routers

            return initialize_routers(routers)

        except Exception as e:
            print('INFO', str(e))
            return routers
