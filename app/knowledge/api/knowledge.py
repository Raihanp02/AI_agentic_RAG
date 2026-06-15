from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from concurrent.futures import ProcessPoolExecutor
import uuid
from typing import List

from app.knowledge.service.add_knowledge.pipeline import KnowledgePipeline, knowledge_pipeline
from app.knowledge.schema.knowledge_response import KnowledgeResponse
from core.database.session import get_db_fastapi
from core.state import progress_dict
from app.knowledge.service.progress_service import update_progress

router = APIRouter()
pool = ProcessPoolExecutor(max_workers=2)

@router.post("/insert-knowledge")
async def insert_knowledge(source: List[UploadFile] = File(...), category: str = None):
    jobs = []
    for file in source:
        doc = await file.read()
        filename = file.filename
        job_id = str(uuid.uuid4())

        pool.submit(knowledge_pipeline.process_document, doc, category, job_id, filename, progress_dict=progress_dict)
        jobs.append(job_id)

        update_progress(progress_dict, job_id, filename=filename, status="Loading model...")

    return {"message": "Documents are being processed", "job_ids": jobs}

    # return knowledge_pipeline.process_document(session, await source[0].read(), category, filename=source[0].filename)

@router.get("/progresses")
async def get_progresses():
    return progress_dict