from ...database.models.vectorstore import Chunk
from ...database.models.relational import Document

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
    session.refresh(chunk)

    return chunk

def store_document(session, document_id, title, source_url, category=None):
    document = Document(
        id=document_id,
        title=title,
        source_url=source_url,
        category=category
    )
    session.add(document)
    session.commit()
    session.refresh(document)

    return document
