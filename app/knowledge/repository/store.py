from ..models.vectorstore import Chunk
from ..models.relational import Document

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

from sqlalchemy import insert

def store_embeddings_bulk_sync(session, document_id, chunks, batch_size=500):
    """
    Bulk insert chunks for one document.

    chunks: list of dicts with keys:
        - content (str)
        - embedding (list[float] | np.ndarray)
        - chunk_index (int)
        - extra_data (dict, optional)

    Returns the list of inserted Chunk ids, in input order.
    """
    if not chunks:
        return []

    try:
        rows = [
            {
                "document_id": document_id,
                "content": c["content"],
                "embedding": c["embedding"],
                "chunk_index": c["chunk_index"],
                "extra_data": c.get("extra_data") or {},
            }
            for c in chunks
        ]

        inserted_ids = []
        for i in range(0, len(rows), batch_size):
            batch = rows[i : i + batch_size]
            result = session.execute(insert(Chunk).returning(Chunk.id), batch)
            inserted_ids.extend(result.scalars().all())

        session.flush()
        return inserted_ids
    except Exception as e:
        session.rollback()
        raise e
