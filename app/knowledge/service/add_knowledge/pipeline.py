from .chunk_embedder import HuggingFaceTextEmbedder
from .doc_chunker import DoclingHybridChunker
from .doc_parser import DoclingParser
from ..crud_knowledge.store import store_embedding, store_document

from fastapi import UploadFile
from pathlib import Path

class KnowledgePipeline:
    BASE_DIR = Path(__file__).resolve().parents[2]
    def __init__(self, doc_parser = DoclingParser(), chunker = DoclingHybridChunker(), chunk_embedder = HuggingFaceTextEmbedder()):
        self.doc_parser = doc_parser
        self.chunker = chunker
        self.chunk_embedder = chunk_embedder

    def process_document(self, session, document):
        filename = self._extract_filename(document)
        # Step 1: Parse the document
        parsed_content = self.doc_parser.parse(document)
        markdown_content = self.doc_parser.extract_markdown(parsed_content)
        title = self.doc_parser.extract_title(markdown_content, filename)

        # Store document metadata in the database
        source_url = self._save_document_locally(document)
        document_result = store_document(session, title=title, content = markdown_content, source_url=source_url.relative_to(self.BASE_DIR).as_posix())

        # Step 2: Chunk the parsed content
        chunks = self.chunker.chunk(parsed_content)

        # Step 3: Embed the chunks
        for i, chunk in enumerate(chunks):
            embedded_chunk = self.chunk_embedder.embed(chunk)

            # Step 4: Store the embedded chunks in the database
            store_embedding(session, document_id=document_result.id, content=chunk, embedding=embedded_chunk, chunk_index=i)

        return {
            "message": "Document processed and stored successfully",
            "document_id": document_result.id,
            "title": title,
            "source_url": source_url.relative_to(self.BASE_DIR).as_posix(),
            "num_chunks": len(chunks)
        }
    
    def _extract_filename(self, file):
        if isinstance(file, UploadFile):
            return file.filename
        else:
            return Path(file).name
        
    def _save_document_locally(self, document, save_dir=BASE_DIR / "app" / "knowledge" / "database" / "upload"):
        save_dir.mkdir(parents=False, exist_ok=True)

        filename = self._extract_filename(document)
        save_path = Path(save_dir) / filename

        if isinstance(document, UploadFile):
            with open(save_path, 'wb') as f:
                f.write(document.file.read())
        else:
            with open(document, 'rb') as src, open(save_path, 'wb') as dst:
                while chunk := src.read(1024 * 1024):  # 1MB
                    dst.write(chunk)

        return save_path