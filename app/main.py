from fastapi import FastAPI
from app.llm.routers import api_router as llm_router
from app.knowledge.routers import api_router as knowledge_router

app = FastAPI()

app.include_router(llm_router, prefix="/api")
app.include_router(knowledge_router, prefix="/api")