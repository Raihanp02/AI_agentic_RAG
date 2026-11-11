import logging
import shutil
import uuid
from functools import lru_cache
from pathlib import Path

from fastapi import UploadFile

from provider.text_embedding.embedder import get_embedder
from .doc_chunker import DoclingHybridChunker
from .doc_parser import DoclingParser
from repository.store import (
    store_document_sync,
    store_embeddings_bulk_sync,   # the new bulk function you need to write
)
from ..progress_service.reporter import ProgressReporter, NullReporter
from core.database.session import get_sync_db

logger = logging.getLogger(__name__)


class KnowledgePipeline:
    BASE_DIR = Path(__file__).resolve().parents[4]
    UPLOAD_DIR = BASE_DIR / "core" / "database" / "upload"

    def __init__(self, doc_parser=None, chunker=None, chunk_embedder=None):
        self.doc_parser = doc_parser or DoclingParser()
        self.chunker = chunker or DoclingHybridChunker()
        self.chunk_embedder = chunk_embedder or get_embedder()

    def process_document(
        self,
        document,
        category: str | None = None,
        filename: str | None = None,
        progress: ProgressReporter | None = None,
    ):
        progress = progress or NullReporter()
        save_path = None
        try:
            filename = Path(filename or self._extract_filename(document)).name

            # 1. Save first, so everything downstream works from a stable file
            save_path = self._save_document_locally(document, filename)

            # 2. Parse
            progress.stage("Parsing document...")
            parsed = self.doc_parser.parse(save_path, filename)
            markdown = self.doc_parser.extract_markdown(parsed)
            title = self.doc_parser.extract_title(markdown, filename)

            # 3. Chunk
            progress.stage("Chunking document...")
            chunks = self.chunker.chunk(parsed)
            if not chunks:
                raise ValueError("No content could be extracted from the document")

            # 4. Embed in batches (no DB connection held)
            progress.stage("Embedding chunks...", total=len(chunks))
            vectors = self.chunk_embedder.embed_many(chunks)

            # 5. Short transaction: document + all chunks, atomically
            progress.stage("Saving...")
            rel_path = save_path.relative_to(self.BASE_DIR).as_posix()
            with get_sync_db() as session:
                doc = store_document_sync(
                    session, title=title, source_url=rel_path, category=category
                )
                store_embeddings_bulk_sync(
                    session,
                    document_id=doc.id,
                    chunks=[
                        {"chunk_index": i, "content": c, "embedding": v}
                        for i, (c, v) in enumerate(zip(chunks, vectors))
                    ]
                )

            progress.succeed()
            return {
                "message": "Document processed and stored successfully",
                "document_id": doc.id,
                "title": title,
                "source_url": rel_path,
                "num_chunks": len(chunks),
            }

        except Exception as e:
            logger.exception("Knowledge pipeline failed for %s", filename)
            progress.fail(e)
            if save_path:
                save_path.unlink(missing_ok=True)
            raise

    def _extract_filename(self, file):
        if isinstance(file, UploadFile):
            return file.filename
        if isinstance(file, (str, Path)):
            return Path(file).name
        raise ValueError("filename is required when passing raw bytes")

    def _save_document_locally(self, document, filename):
        self.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        save_path = self.UPLOAD_DIR / f"{uuid.uuid4().hex}_{filename}"

        if isinstance(document, UploadFile):
            document.file.seek(0)
            with open(save_path, "wb") as dst:
                shutil.copyfileobj(document.file, dst)
        elif isinstance(document, bytes):
            save_path.write_bytes(document)
        else:
            shutil.copyfile(document, save_path)
        return save_path


@lru_cache(maxsize=1)
def get_knowledge_pipeline() -> KnowledgePipeline:
    return KnowledgePipeline()