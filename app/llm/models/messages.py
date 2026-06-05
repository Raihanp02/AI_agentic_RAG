from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, String, Text, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship, Mapped

from core.database.base import Base
import uuid

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True)      # internal DB key
    uuid = Column(UUID(as_uuid=True), unique=True, index=True, default=uuid.uuid4)

    conversation_id = Column(
        Integer,
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)

    metadata_json = Column(
        JSONB,
        nullable=True
    )

    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    conversation: Mapped["Conversation"] = relationship(
        "Conversation",
        back_populates="messages"
    )