from sqlalchemy import Column, Integer, ForeignKey, Text, Column, DateTime, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship, Mapped
from datetime import datetime

from core.database.base import Base
import uuid 

class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(Integer, primary_key=True)      # internal DB key
    uuid = Column(UUID(as_uuid=True), unique=True, index=True, default=uuid.uuid4)

    user_id = Column(Integer, nullable=False, index=True)

    title = Column(String(255), nullable=True, default="New Conversation")

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