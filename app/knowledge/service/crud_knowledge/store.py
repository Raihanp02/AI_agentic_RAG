from ...database.models.vectorstore import Chunk
from ...database.models.relational import Document

# ✅ Async versions — for FastAPI routes
async def store_document(session, title, source_url, category=None):
    try:
        document = Document(title=title, source_url=source_url, category=category)
        session.add(document)
        await session.flush()
        await session.refresh(document)
        return document
    except Exception as e:
        await session.rollback()
        raise e

async def store_embedding(session, document_id, content, embedding, chunk_index, extra_data=None):
    try:
        chunk = Chunk(document_id=document_id, content=content, embedding=embedding, chunk_index=chunk_index, extra_data=extra_data or {})
        session.add(chunk)
        await session.flush()
        await session.refresh(chunk)
        return chunk
    except Exception as e:
        await session.rollback()
        raise e

# ✅ Sync versions — for ProcessPoolExecutor
def store_document_sync(session, title, source_url, category=None):
    try:
        document = Document(title=title, source_url=source_url, category=category)
        session.add(document)
        session.flush()
        session.refresh(document)
        return document
    except Exception as e:
        session.rollback()
        raise e

def store_embedding_sync(session, document_id, content, embedding, chunk_index, extra_data=None):
    try:
        chunk = Chunk(document_id=document_id, content=content, embedding=embedding, chunk_index=chunk_index, extra_data=extra_data or {})
        session.add(chunk)
        session.flush()
        session.refresh(chunk)
        return chunk
    except Exception as e:
        session.rollback()
        raise e
