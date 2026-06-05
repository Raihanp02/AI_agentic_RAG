from fastapi import APIRouter, Depends, HTTPException
from langchain_core.messages import HumanMessage
import traceback
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.llm.service.agent_graph import chat_graph
from app.llm.schema.agent_request import AgentRequest
from app.llm.schema.conversation import ConversationDetail, MessageDetail, MessageResponse, MessageListResponse, validate_conversation_id
from app.llm.service.message_manager import add_message, add_conversation, get_conversation, get_list_conversations
from app.user.models.users import User
from core.database.session import get_db_fastapi
from app.user.services.auth import get_current_active_user
from sqlalchemy import select

router = APIRouter()

@router.post("/conversations", response_model=ConversationDetail)
async def create_conversation(current_user: User = Depends(get_current_active_user), title: str = None, db: AsyncSession = Depends(get_db_fastapi)):
    conversation = await add_conversation(db, current_user.id, title)
    return conversation

@router.get("/conversations", response_model=list[ConversationDetail])
async def get_conversations_list(current_user: User = Depends(get_current_active_user), db: AsyncSession = Depends(get_db_fastapi)):
    return await get_list_conversations(db, current_user.id)

@router.get("/conversation/{conversation_uuid}", response_model=ConversationDetail)
async def get_conversation_detail(conversation_uuid: UUID, current_user: User = Depends(get_current_active_user), db: AsyncSession = Depends(get_db_fastapi)):
    conversation = await get_conversation(db, conversation_uuid, user_id=current_user.id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return conversation

@router.get("/conversation/{conversation_uuid}/messages", response_model=MessageListResponse)
async def get_conversation_messages(conversation_uuid: UUID, current_user: User = Depends(get_current_active_user), db: AsyncSession = Depends(get_db_fastapi)):
    conversation = await get_conversation(db, conversation_uuid, user_id=current_user.id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return conversation

@router.post("/conversation/{conversation_uuid}/messages", response_model=MessageResponse)
async def chat(req: AgentRequest, conversation_uuid: UUID = Depends(validate_conversation_id), current_user: User = Depends(get_current_active_user), db: AsyncSession = Depends(get_db_fastapi)):
    try:
        result = await chat_graph.graph.ainvoke(
            {"messages": [HumanMessage(content=req.messages)]},
            {"configurable": {"thread_id": conversation_uuid}}
        )
        role = result["messages"][-1].type
        content = result["messages"][-1].content

        await add_message(db, conversation_uuid, role, content)

        return {
            "message": content
        }
    except Exception as e:
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )