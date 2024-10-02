from urllib.parse import urljoin
from fastapi import Header, Request


def build_qualified_url(base_url: str = Header(None), relative_path: str = ...) -> str:
    if not base_url.startswith(('http://', 'http://')):
        base_url = 'http://' + base_url

    return urljoin(base_url, relative_path)


def get_original_host(request: Request, origin: str = Header(None)):
    if origin:
        return origin
    return request.headers.get('referer')
