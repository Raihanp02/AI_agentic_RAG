from app.knowledge.schema.document_response import DocumentResponse
from core.schemas.paginated_response import PaginatedResponseBase

class DocumentListResponse(PaginatedResponseBase):
    items: list[DocumentResponse]