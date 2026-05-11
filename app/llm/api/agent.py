from fastapi import APIRouter, Depends, HTTPException
from langchain_core.messages import HumanMessage
import traceback

from app.llm.service.agent_graph import chat_graph
from app.llm.schema.agent_request import AgentRequest

router = APIRouter()

@router.post("/chat")
async def chat(req: AgentRequest):
    try:
        result = await chat_graph.graph.ainvoke(
            {"messages": [HumanMessage(content=req.messages)]},
            {"configurable": {"thread_id": "4"}}
        )

        return result
    except Exception as e:
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )