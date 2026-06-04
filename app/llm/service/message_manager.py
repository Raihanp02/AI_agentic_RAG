from sqlalchemy import select

from app.llm.models.conversations import Conversation
from app.llm.models.messages import Message

def add_conversation(session, user_id, title=None):
    conversation = Conversation(user_id=user_id, title=title)
    session.add(conversation)
    session.commit()
    session.refresh(conversation)
    return conversation

def add_message(session, conversation_id, role, content, metadata_json=None):
    message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
        metadata_json=metadata_json
    )
    session.add(message)
    session.commit()
    session.refresh(message)
    return message

def get_conversation(session, conversation_id, user_id=None) -> Conversation:
    query = select(Conversation).where(Conversation.id == conversation_id)
    if user_id is not None:
        query = query.where(Conversation.user_id == user_id)
        
    return session.execute(query).scalars().first()

def get_list_conversations(session, user_id) -> list[Conversation]:
    query = select(Conversation).where(Conversation.user_id == user_id)
    query = query.order_by(Conversation.created_at.desc())
    return session.execute(query).scalars().all()