# progress_service/schemas.py
from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field, computed_field


def _now() -> datetime:
    return datetime.now(timezone.utc)


class JobState(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"

    @property
    def is_terminal(self) -> bool:
        return self in (JobState.SUCCEEDED, JobState.FAILED)


class IngestionResult(BaseModel):
    message: str
    document_id: int | str        # match your DB id type
    title: str
    source_url: str
    num_chunks: int


class JobRecord(BaseModel):
    job_id: str
    state: JobState = JobState.QUEUED
    filename: str | None = None
    status: str = "Queued"                  # human-readable message
    processed_chunks: int = 0
    total_chunks: int | None = None         # None = unknown yet (indeterminate)
    error: str | None = None
    result: IngestionResult | None = None
    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)

    @computed_field
    @property
    def percent(self) -> float | None:
        if not self.total_chunks:
            return None
        return round(self.processed_chunks / self.total_chunks * 100, 1)


class JobSummary(BaseModel):
    job_id: str
    state: JobState
    filename: str | None
    status: str
    processed_chunks: int
    total_chunks: int | None
    created_at: datetime
    updated_at: datetime

    @computed_field
    @property
    def percent(self) -> float | None:
        if not self.total_chunks:
            return None
        return round(self.processed_chunks / self.total_chunks * 100, 1)