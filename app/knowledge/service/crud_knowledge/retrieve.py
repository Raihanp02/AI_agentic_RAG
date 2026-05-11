from sqlalchemy import select
import numpy as np
from app.knowledge.database.models.vectorstore import Chunk
from app.knowledge.database.models.relational import Document

async def get_document_from_embedding(session, embedding: list[float] | np.ndarray, top_k: int = 1, category: str = None):
    if isinstance(embedding, np.ndarray):
        embedding = embedding.astype(float).tolist()

    stmt = select(Chunk)

    if category:
        stmt = (
            stmt
            .join(Chunk.document)
            .where(Document.cagegory == category)
        )
    
    similarity_expr = 1 - Chunk.embedding.cosine_distance(embedding)

    stmt = (
        stmt
        .order_by(similarity_expr)
        .limit(top_k)
    )

    results = await session.execute(stmt).scalars().all()

    return results