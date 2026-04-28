from fastapi import APIRouter, Depends, UploadFile, File
from app.knowledge.service.add_knowledge.pipeline import KnowledgePipeline
from app.knowledge.schema.knowledge_response import KnowledgeResponse

router = APIRouter()
knowledge_pipeline = KnowledgePipeline()

@router.post("/insert-knowledge", response_model=KnowledgeResponse)
async def insert_knowledge(source: UploadFile = File(...), category: str = None):
    return knowledge_pipeline.process_document(source, category)