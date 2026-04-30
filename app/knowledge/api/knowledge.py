from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session

from app.knowledge.service.add_knowledge.pipeline import KnowledgePipeline
from app.knowledge.schema.knowledge_response import KnowledgeResponse
from app.knowledge.database.session import get_db_fastapi

router = APIRouter()
knowledge_pipeline = KnowledgePipeline()

@router.post("/insert-knowledge", response_model=KnowledgeResponse)
async def insert_knowledge(session: Session = Depends(get_db_fastapi), source: UploadFile = File(...), category: str = None):
    return knowledge_pipeline.process_document(session, source, category)