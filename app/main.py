from fastapi import FastAPI
from contextlib import asynccontextmanager
from asyncpg import Connection as AsyncConnection
from psycopg_pool import AsyncConnectionPool
import psycopg
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from psycopg.rows import dict_row


from app.agent.routers import api_router as llm_router
from app.knowledge.routers import api_router as knowledge_router
from app.user.routers import api_router as auth_router

from app.agent.service.agent_tools.rag_tools import rag_tools
from core.config import settings
from app.agent.service.graph.agent_graph import AgenticRAGGraph
from app.provider.factory import get_llm

@asynccontextmanager
async def lifespan(app: FastAPI):
    db_uri = settings.DATABASE_SYNC_URL  # plain postgresql://...
    conn_kwargs = {
        "autocommit": True,
        "row_factory": dict_row,
        "options": "-c search_path=langgraph",
    }

    # one-off: schema + tables
    async with await psycopg.AsyncConnection.connect(db_uri, **conn_kwargs | {"options": None}) as conn:
        await conn.execute("CREATE SCHEMA IF NOT EXISTS langgraph")

    async with AsyncConnectionPool(
        conninfo=db_uri,
        max_size=5,
        kwargs=conn_kwargs,
        open=False,
    ) as pool:
        checkpointer = AsyncPostgresSaver(pool)
        await checkpointer.setup()

        app.state.chat_graph = AgenticRAGGraph(
            llm=get_llm(), tools=[rag_tools], checkpointer=checkpointer
        )
        yield

app = FastAPI(lifespan=lifespan)

app.include_router(auth_router, prefix="/api")
app.include_router(llm_router, prefix="/api")
app.include_router(knowledge_router, prefix="/api")