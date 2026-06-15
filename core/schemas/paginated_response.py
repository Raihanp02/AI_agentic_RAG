from pydantic import BaseModel


class PaginatedResponseBase(BaseModel):
    total: int
    page: int
    size: int
    pages: int