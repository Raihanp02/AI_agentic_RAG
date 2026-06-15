from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from concurrent.futures import ProcessPoolExecutor
import uuid
from typing import List
from fastapi_filter import FilterDepends
from sqlalchemy import select
from starlette import status

from app.knowledge.service.add_knowledge.pipeline import KnowledgePipeline, knowledge_pipeline
from app.knowledge.schema.document_list_response import DocumentListResponse
from app.knowledge.filters.document_knowledge import DocumentFilter
from app.knowledge.models import Document
from app.knowledge.service.crud_knowledge.retrieve import delete_document_by_id
from core.utils.pagination import paginate
from core.database.session import get_db_fastapi
from core.state import progress_dict
from app.knowledge.service.progress_service import update_progress
from app.user.services.auth import get_current_active_user
from app.user.models import User


router = APIRouter()
pool = ProcessPoolExecutor(max_workers=2)

@router.get("/knowledge", response_model=DocumentListResponse)
async def get_knowledge_document_list(
    db: AsyncSession = Depends(get_db_fastapi),
    page: int = 1,
    size: int = 10,
    show_all: bool = False,
    attendance_filter: DocumentFilter = FilterDepends(DocumentFilter),
    current_user: User = Depends(get_current_active_user),
    ):
    statement = select(Document)

    if show_all:
        pass

    statement = attendance_filter.filter(statement)
    statement = attendance_filter.sort(statement)

    return await paginate(session=db, statement=statement, page=page, page_size=size)

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

@router.delete("/knowledge/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_knowledge(document_id: int, db: AsyncSession = Depends(get_db_fastapi), current_user: User = Depends(get_current_active_user)):
    return await delete_document_by_id(db, document_id)