from ..models.vectorstore import Chunk
from ..models.relational import Document

def store_embedding(session, document_id, content, embedding, chunk_index, extra_data=None):
    chunk = Chunk(
        document_id=document_id,
        content=content,
        embedding=embedding,
        chunk_index=chunk_index,
        extra_data=extra_data or {}
    )
    session.add(chunk)
    session.commit()
    return chunk.id

def store_document(session, document_id, title, source_url):
    document = Document(
        id=document_id,
        title=title,
        source_url=source_url
    )
    session.add(document)
    session.commit()
    return document.id
