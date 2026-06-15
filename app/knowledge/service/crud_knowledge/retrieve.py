from sqlalchemy import select
import numpy as np
from app.knowledge.models.vectorstore import Chunk
from app.knowledge.models.relational import Document

async def get_document_from_embedding(session, embedding: list[float] | np.ndarray, top_k: int = 1, category: str = None):
    if isinstance(embedding, np.ndarray):
        embedding = embedding.astype(float).tolist()

    stmt = select(Chunk)

    if category:
        stmt = (
            stmt
            .join(Chunk.document)
            .where(Document.category == category)
        )
    
    similarity_expr = 1 - Chunk.embedding.cosine_distance(embedding)

    stmt = (
        stmt
        .order_by(similarity_expr.desc())
        .limit(top_k)
    )

    results = await session.execute(stmt)
    results = results.scalars().all()

    return results

async def get_document_by_id(session, document_id: int):
    stmt = select(Document).where(Document.id == document_id)
    result = await session.execute(stmt).scalars().first()
    return result

async def delete_document_by_id(session, document_id: int):
    stmt = select(Document).where(Document.id == document_id)
    result = await session.execute(stmt)
    document = result.scalars().first()

    if not document:
        return False

    await session.delete(document)
    await session.commit()