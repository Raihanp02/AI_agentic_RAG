from fastapi import APIRouter
from app.llm.api import agent

api_router = APIRouter()

api_router.include_router(agent.router, tags=["chat"])