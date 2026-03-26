from sqlalchemy import Column, Integer, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from ..base import Base

class Chunk(Base):
    __tablename__ = "chunks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    content = Column(Text)
    embedding = Column(Vector(512)) 
    chunk_index = Column(Integer)
    extra_data = Column(JSONB)

    document = relationship("Document", back_populates="chunks")
