from fastapi import APIRouter, Depends

from app.llm.service.agent_graph import chat_graph
from app.llm.schema.agent_request import AgentRequest

router = APIRouter()

@router.post("/chat")
async def chat(req: AgentRequest):
    result = chat_graph.graph.invoke({
        "message": req.message
    })

    return result