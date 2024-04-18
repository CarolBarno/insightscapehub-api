from pathlib import Path
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from insightscapehub.utils import settings
from insightscapehub.utils.enums import stringify

docs_router = APIRouter(include_in_schema=False)
directory = Path(__file__).joinpath('../templates').resolve()
templates = Jinja2Templates(directory)


@docs_router.get('/docs/', response_class=HTMLResponse)
def view_documentation(request: Request):
    root = getattr(settings, 'APP_PREFIX', '')
    url = root + '/openapi.json'

    return templates.TemplateResponse('docs.html', {'request': request, 'schema_url': url, 'title': stringify(settings.APP_NAME)})
