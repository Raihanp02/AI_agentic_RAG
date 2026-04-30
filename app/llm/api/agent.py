from fastapi import APIRouter, Depends
from langchain_core.messages import HumanMessage

from app.llm.service.agent_graph import chat_graph
from app.llm.schema.agent_request import AgentRequest

router = APIRouter()

@router.post("/chat")
async def chat(req: AgentRequest):
    result = await chat_graph.graph.ainvoke(
        {"messages": [HumanMessage(content=req.messages)]},
        {"configurable": {"thread_id": "4"}}
    )

    return result