from pydantic import BaseModel

class KnowledgeResponse(BaseModel):
    message: str
    documents_id: int
    title: str
    source_url: str
    num_chunks: int