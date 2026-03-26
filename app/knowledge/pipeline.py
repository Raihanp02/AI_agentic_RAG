from .chunk_embedder import HuggingFaceTextEmbedder
from .doc_chunker import DoclingHybridChunker
from .doc_parser import DoclingParser
from .database.crud.store import store_embedding, store_metadata

from fastapi import UploadFile
from pathlib import Path

class KnowledgePipeline:
    def __init__(self, doc_parser, chunker, chunk_embedder, db):
        self.doc_parser = doc_parser
        self.chunker = chunker
        self.chunk_embedder = chunk_embedder
        self.db = db

    def process_document(self, session, document):
        filename = self._extract_filename(document)
        # Step 1: Parse the document
        parsed_content = self.doc_parser.parse(document)
        markdown_content = self.doc_parser(parsed_content)
        title = self.doc_parser.extract_title(markdown_content, document.source_url)

        # Step 2: Chunk the parsed content
        chunks = self.chunker.chunk(parsed_content)

        # Step 3: Embed the chunks
        for i, chunk in enumerate(chunks):
            embedded_chunk = self.chunk_embedder.embed(chunk)

            # Step 4: Store the embedded chunks in the database
            store_embedding(session, document_id=document.id, content=chunk, embedding=embedded_chunk, chunk_index=i)

        return chunks
    
    def _extract_filename(self, file):
        if isinstance(file, UploadFile):
            return file.filename
        else:
            return Path(file).name