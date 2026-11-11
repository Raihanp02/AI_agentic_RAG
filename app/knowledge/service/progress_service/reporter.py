import time
from typing import Protocol

from .store import ProgressStore


class ProgressReporter(Protocol):
    def stage(self, name: str, *, total: int | None = None) -> None: ...
    def advance(self, n: int = 1) -> None: ...
    def succeed(self) -> None: ...
    def fail(self, error: Exception) -> None: ...


class NullReporter:
    """Used when there's no job to report to."""
    def stage(self, name, *, total=None): pass
    def advance(self, n=1): pass
    def succeed(self): pass
    def fail(self, error): pass


class JobProgressReporter:
    def __init__(self, store: ProgressStore, job_id: str, filename=None, min_interval=0.5):
        self._store = store
        self._job_id = job_id
        self._min_interval = min_interval
        self._processed = 0
        self._total = None
        self._last_write = 0.0
        self._write(state="running", **({"filename": filename} if filename else {}))

    def _write(self, **fields):
        self._store.update(self._job_id, **fields)   # was: update_progress(...)
        self._last_write = time.monotonic()

    def stage(self, name, *, total=None):
        self._processed, self._total = 0, total
        fields = {"status": name, "processed_chunks": 0}
        if total is not None:
            fields["total_chunks"] = total
        self._write(**fields)                # stage changes are never throttled

    def advance(self, n=1):
        self._processed += n
        done = self._total is not None and self._processed >= self._total
        if done or time.monotonic() - self._last_write >= self._min_interval:
            self._write(processed_chunks=self._processed)

    def succeed(self):
        self._write(state="succeeded", status="Document processed successfully",
                    processed_chunks=self._processed)

    def fail(self, error):
        self._write(state="failed", status="Failed", error=str(error))