from fastapi import APIRouter
from app.knowledge.api import knowledge

api_router = APIRouter()

api_router.include_router(knowledge.router, tags=["chat"])