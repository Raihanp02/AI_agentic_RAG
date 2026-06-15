from pydantic import BaseModel
from datetime import datetime

class DocumentResponse(BaseModel):
    id: int
    title: str
    source_url: str
    category: str | None = None
    created_at: datetime