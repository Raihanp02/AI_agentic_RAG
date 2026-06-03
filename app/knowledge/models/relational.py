from sqlalchemy import Column, Integer, ForeignKey, Text, Column, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship, Mapped
from datetime import datetime
from pgvector.sqlalchemy import Vector

from core.database.base import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(Text)
    category = Column(Text, nullable=True)
    source_url = Column(Text)
    extra_data = Column(JSONB, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    chunks: Mapped[list["Chunk"]] = relationship(
        "Chunk", 
        back_populates="document", 
        cascade="all, delete-orphan"
    )
