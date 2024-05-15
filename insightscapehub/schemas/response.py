from pydantic import BaseModel


class PageInfo(BaseModel):
    page: int
    has_next: bool
    has_previous: bool
    page_count: int
    total_count: int
    total_pages: int


class Response(BaseModel):
    page_info: PageInfo

    class Config:
        from_attributes = True
        json_schema_extra = {
            'example': {
                'results': [],
                'page_info': {
                    'page': 1,
                    'has_next': True,
                    'has_previous': True,
                    'page_count': 10,
                    'total_count': 10,
                    'total_pages': 1
                }
            }
        }
