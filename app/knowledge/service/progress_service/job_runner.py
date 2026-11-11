# services/job_runner.py
import logging
import uuid
from concurrent.futures import ThreadPoolExecutor

from progress_service.reporter import JobProgressReporter
from progress_service.store import ProgressStore

logger = logging.getLogger(__name__)


class IngestionJobRunner:
    def __init__(self, pipeline, store: ProgressStore, max_workers: int = 1):
        self._pipeline = pipeline
        self._store = store
        self._pool = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="ingest")

    def submit(self, data: bytes, filename: str, category: str | None = None) -> str:
        job_id = uuid.uuid4().hex
        # create the entry before submit so the worker can't race it
        self._store.create(job_id, state="queued", filename=filename, status="Queued",
                           processed_chunks=0, total_chunks=None)
        self._pool.submit(self._run, job_id, data, filename, category)
        return job_id

    def _run(self, job_id, data, filename, category):
        reporter = JobProgressReporter(self._store, job_id, filename=filename)
        try:
            result = self._pipeline.process_document(
                data, category=category, filename=filename, progress=reporter
            )
            self._store.update(job_id, result=result)
        except Exception:
            # the pipeline already called reporter.fail(); just log here
            logger.exception("Job %s failed", job_id)

    def shutdown(self):
        self._pool.shutdown(wait=False, cancel_futures=True)

