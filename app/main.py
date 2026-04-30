from fastapi import FastAPI
from contextlib import asynccontextmanager
from asyncpg import Connection as AsyncConnection
from psycopg_pool import AsyncConnectionPool
import psycopg

from app.llm.routers import api_router as llm_router
from app.knowledge.routers import api_router as knowledge_router
from core.config import settings
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from app.llm.service.agent_graph import chat_graph

@asynccontextmanager
async def lifespan(app: FastAPI):
    # use plain URL for psycopg/langgraph
    db_uri = f"{settings.DATABASE_SYNC_URL}?options=-csearch_path%3Dlanggraph"
    
    async with await psycopg.AsyncConnection.connect(db_uri, autocommit=True) as conn:
        await AsyncPostgresSaver(conn).setup()

    async with AsyncConnectionPool(conninfo=db_uri, max_size=5) as pool:
        checkpointer = AsyncPostgresSaver(pool)
        chat_graph.graph.checkpointer = checkpointer
        yield

app = FastAPI(lifespan=lifespan)

app.include_router(llm_router, prefix="/api")
app.include_router(knowledge_router, prefix="/api")