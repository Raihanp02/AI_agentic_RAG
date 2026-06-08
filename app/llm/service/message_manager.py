from sqlalchemy import select
from sqlalchemy.orm import selectinload
from psycopg_pool import AsyncConnectionPool

from app.llm.models.conversations import Conversation
from app.llm.models.messages import Message

async def add_conversation(session, user_id, title=None):
    conversation = Conversation(user_id=user_id, title=title)
    session.add(conversation)
    await session.commit()
    await session.refresh(conversation)
    return conversation

async def add_message(session, conversation_uuid, role, content, metadata_json=None):
    obj = await get_conversation(session, conversation_uuid)

    message = Message(
        conversation_id=obj.id,
        role=role,
        content=content,
        metadata_json=metadata_json
    )
    session.add(message)
    await session.commit()
    await session.refresh(message)
    return message

async def get_conversation(session, conversation_uuid, user_id=None) -> Conversation:
    query = select(Conversation).where(Conversation.uuid == conversation_uuid)
    if user_id is not None:
        query = query.where(Conversation.user_id == user_id)

    query = query.options(
        selectinload(Conversation.messages)
    )
        
    return (await session.execute(query)).scalars().first()

async def get_list_conversations(session, user_id) -> list[Conversation]:
    query = select(Conversation).where(Conversation.user_id == user_id)
    query = query.order_by(Conversation.created_at.desc())

    return (await session.execute(query)).scalars().all()

async def delete_checkpoint(pool: AsyncConnectionPool, conversation_id: str):
    async with pool.connection() as conn:
        await conn.execute(
            "DELETE FROM checkpoints WHERE thread_id = %s", (str(conversation_id),)
        )
        await conn.execute(
            "DELETE FROM checkpoint_writes WHERE thread_id = %s", (str(conversation_id),)
        )
        await conn.execute(
            "DELETE FROM checkpoint_blobs WHERE thread_id = %s", (str(conversation_id),)
        )

async def delete_conversation(session, conversation_uuid, user_id):
    conversation = await get_conversation(session, conversation_uuid, user_id)
    if not conversation:
        return None

    await session.delete(conversation)
    await session.commit()
    return True