from pydantic import BaseModel
from datetime import datetime
from app.user.models.users import User
from app.llm.models.conversations import Conversation
from app.user.services.auth import get_current_active_user
from core.database.session import get_db_fastapi

from fastapi import Depends, HTTPException

class ConversationDetail(BaseModel):
    id: int
    user_id: int
    title: str = "New Conversation"
    created_at: datetime

    class Config:
        from_attributes = True

class ConversationList(BaseModel):
    conversations: list[ConversationDetail]

    class Config:
        from_attributes = True

class MessageDetail(BaseModel):
    id: int
    conversation_id: int
    role: str
    content: str
    metadata_json: str | None = None

    class Config:
        from_attributes = True

class ConversationMessages(BaseModel):
    messages: list[MessageDetail]

    class Config:
        from_attributes = True

def validate_conversation_id(
        conversation_id: int,
        db = Depends(get_db_fastapi),
        current_user: User = Depends(get_current_active_user),
    ) -> Conversation:

    conversation = (
        db.query(Conversation)
        .filter(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id
        )
        .first()
    )

    if conversation is None:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found"
        )

    return conversation