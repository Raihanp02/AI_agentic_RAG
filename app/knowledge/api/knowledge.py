from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from concurrent.futures import ProcessPoolExecutor
import uuid
from typing import List
from fastapi_filter import FilterDepends
from sqlalchemy import select
from starlette import status
from fastapi import Query

from app.knowledge.service.add_knowledge.pipeline import KnowledgePipeline, knowledge_pipeline
from app.knowledge.schema.document_list_response import DocumentListResponse
from app.knowledge.filters.document_knowledge import DocumentFilter
from app.knowledge.models import Document
from app.knowledge.repository.retrieve import delete_document_by_id
from core.utils.pagination import paginate
from core.database.session import get_db_fastapi
from app.user.services.auth import get_current_active_user
from app.user.models import User
from app.knowledge.service.progress_service.job_runner import IngestionJobRunner
from app.knowledge.service.progress_service.store import ProgressStore, get_progress_store
from app.knowledge.schema.progress import JobSummary, JobState
from dependencies import get_job_runner

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

@router.post("/insert-knowledge", status_code=202)
async def insert_knowledge(
    source: list[UploadFile] = File(...),
    category: str | None = None,
    runner: IngestionJobRunner = Depends(get_job_runner),
    current_user: User = Depends(get_current_active_user)
):
    job_ids = [runner.submit(await f.read(), f.filename, category) for f in source]
    return {"message": "Documents are being processed", "job_ids": job_ids}

@router.get("/progresses", response_model=list[JobSummary])
async def list_progresses(
    state: JobState | None = JobState.RUNNING,
    limit: int = Query(50, ge=1, le=200),
    store: ProgressStore = Depends(get_progress_store),
    current_user: User = Depends(get_current_active_user)
):
    return [JobSummary.model_validate(r.model_dump(exclude={"percent"}))
            for r in store.list(state=state, limit=limit)]

@router.delete("/knowledge/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_knowledge(document_id: int, db: AsyncSession = Depends(get_db_fastapi), current_user: User = Depends(get_current_active_user)):
    return await delete_document_by_id(db, document_id)