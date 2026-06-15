from pydantic import BaseModel
from datetime import datetime
from app.user.models.users import User
from app.llm.models.conversations import Conversation
from app.user.services.auth import get_current_active_user
from core.database.session import get_db_fastapi

from fastapi import Depends, HTTPException
from uuid import UUID

class ConversationDetail(BaseModel):
    uuid: UUID
    user_id: int
    title: str = "New Conversation"
    created_at: datetime

    class Config:
        from_attributes = True

class MessageDetail(BaseModel):
    uuid: UUID
    role: str
    content: str
    metadata_json: str | None = None

    class Config:
        from_attributes = True

class MessageListResponse(BaseModel):
    messages: list[MessageDetail]

class MessageResponse(BaseModel):
    message: str

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


async def validate_conversation_id(
        conversation_uuid: UUID,
        db: AsyncSession = Depends(get_db_fastapi),
        current_user: User = Depends(get_current_active_user),
    ) -> Conversation:

    query = select(Conversation).where(
        Conversation.uuid == conversation_uuid,
        Conversation.user_id == current_user.id,
    )
    conversation = (await db.execute(query)).scalars().first()

    if conversation is None:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found"
        )

    return conversation_uuid