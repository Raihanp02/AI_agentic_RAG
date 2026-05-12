from .chunk_embedder import HuggingFaceTextEmbedder
from .doc_chunker import DoclingHybridChunker
from .doc_parser import DoclingParser
from ..crud_knowledge.store import store_embedding_sync, store_document_sync
from ..progress_service import update_progress
from app.knowledge.database.session import get_sync_db

from fastapi import UploadFile
from pathlib import Path
import traceback

class KnowledgePipeline:
    BASE_DIR = Path(__file__).resolve().parents[4]
    def __init__(self, doc_parser = DoclingParser(), chunker = DoclingHybridChunker(), chunk_embedder = HuggingFaceTextEmbedder()):
        self.doc_parser = doc_parser
        self.chunker = chunker
        self.chunk_embedder = chunk_embedder

    def process_document(self, document, category=None, job_id=None, filename=None, progress_dict=None):
        try:
            filename = filename or self._extract_filename(document)

            # Step 1: Parse the document
            if job_id:
                update_progress(progress_dict, job_id, filename=filename, status="Parsing document...")

            parsed_content = self.doc_parser.parse(document, filename)
            markdown_content = self.doc_parser.extract_markdown(parsed_content)
            title = self.doc_parser.extract_title(markdown_content, filename)

            with get_sync_db() as session:
                # Store document metadata in the database
                source_url = self._save_document_locally(document, filename=filename)
                document_result = store_document_sync(session, title=title, source_url=source_url.relative_to(self.BASE_DIR).as_posix(), category=category)

                # Step 2: Chunk the parsed content
                if job_id:
                    update_progress(progress_dict, job_id, status="Chunking document...")

                chunks = self.chunker.chunk(parsed_content)

                # Step 3: Embed the chunks
                if job_id:
                    update_progress(progress_dict, job_id, status="Embedding chunks...", total_chunks=len(chunks))

                for i, chunk in enumerate(chunks):
                    if job_id:
                        update_progress(progress_dict, job_id, processed_chunks=i+1)

                    embedded_chunk = self.chunk_embedder.embed(chunk)

                    # Step 4: Store the embedded chunks in the database
                    store_embedding_sync(session, document_id=document_result.id, content=chunk, embedding=embedded_chunk, chunk_index=i)

                if job_id:
                    update_progress(progress_dict, job_id, status="Document processed successfully")  

                return {
                    "message": "Document processed and stored successfully",
                    "document_id": document_result.id,
                    "title": title,
                    "source_url": source_url.relative_to(self.BASE_DIR).as_posix(),
                    "num_chunks": len(chunks)
                }
        except Exception as e:
            traceback.print_exc()  # ✅ print full traceback
            raise e
    
    def _extract_filename(self, file):
        if isinstance(file, UploadFile):
            return file.filename
        else:
            return Path(file).name
        
    def _save_document_locally(self, document, filename=None, save_dir=BASE_DIR / "app" / "knowledge" / "database" / "upload"):
        save_dir.mkdir(parents=False, exist_ok=True)

        filename = filename or self._extract_filename(document)
        save_path = Path(save_dir) / filename

        if isinstance(document, UploadFile):
            with open(save_path, 'wb') as f:
                f.write(document.file.read())

        elif isinstance(document, bytes):  # ✅ handle bytes from await file.read()
            with open(save_path, 'wb') as f:
                f.write(document)

        else:
            with open(document, 'rb') as src, open(save_path, 'wb') as dst:
                while chunk := src.read(1024 * 1024):  # 1MB
                    dst.write(chunk)

        return save_path