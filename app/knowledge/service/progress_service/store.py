# progress_service/store.py
import threading
from datetime import datetime, timedelta, timezone
from typing import Protocol
from functools import lru_cache

from ...schema.progress import JobRecord, JobState


class ProgressStore(Protocol):
    def create(self, job_id: str, **fields) -> None: ...
    def update(self, job_id: str, **fields) -> None: ...
    def get(self, job_id: str) -> JobRecord | None: ...
    def list(self, state: JobState | None = None, limit: int = 50) -> list[JobRecord]: ...

class InMemoryProgressStore:
    def __init__(self, ttl_seconds: int = 3600):
        self._jobs: dict[str, JobRecord] = {}
        self._lock = threading.Lock()
        self._ttl = timedelta(seconds=ttl_seconds)

    def create(self, job_id, **fields):
        with self._lock:
            self._purge()
            self._jobs[job_id] = JobRecord(job_id=job_id, **fields)

    def update(self, job_id, **fields):
        with self._lock:
            rec = self._jobs.get(job_id)
            if rec is None:
                return
            data = rec.model_dump(exclude={"percent"})
            data.update(fields, updated_at=datetime.now(timezone.utc))
            self._jobs[job_id] = JobRecord.model_validate(data)   # validates every write

    def get(self, job_id):
        with self._lock:
            rec = self._jobs.get(job_id)
            return rec.model_copy(deep=True) if rec else None

    def _purge(self):
        cutoff = datetime.now(timezone.utc) - self._ttl
        expired = [k for k, r in self._jobs.items()
                   if r.state.is_terminal and r.updated_at < cutoff]
        for k in expired:
            del self._jobs[k]

@lru_cache(maxsize=1)
def get_progress_store() -> ProgressStore:
    return InMemoryProgressStore()