from sqlalchemy import Column, Integer, ForeignKey, Text, Column, DateTime, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from uuid import uuid4
from sqlalchemy.orm import relationship, Mapped
from datetime import datetime
from pgvector.sqlalchemy import Vector

from core.database.base import Base

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    title = Column(String(255), nullable=True)

    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    messages: Mapped[list["Message"]] = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="Message.created_at"
    )