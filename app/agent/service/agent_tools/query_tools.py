from functools import lru_cache

from langchain.agents import create_agent
from langchain.tools import tool
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
from provider.llm.factory import get_llm

from core.config import settings

SQL_AGENT_PROMPT = (
    "You are a read-only analytics assistant for a PostgreSQL database. "
    "Always inspect the schema before writing queries. Limit results to 20 rows "
    "unless asked otherwise. Never attempt INSERT, UPDATE, DELETE, or DDL."
)


@lru_cache(maxsize=1)
def _get_sql_agent():
    db_uri = (
        f"{settings.DATABASE_SYNC_URL}"
        f"?options=-csearch_path%3D{settings.QUERY_SCHEMA_NAME}"
    )
    db = SQLDatabase.from_uri(db_uri)
    llm = get_llm(provider=settings.QUERY_LLM if settings.QUERY_LLM_URL else settings.LLM_PROVIDER)
    tools = SQLDatabaseToolkit(db=db, llm=llm).get_tools()
    return create_agent(model=llm, tools=tools, system_prompt=SQL_AGENT_PROMPT)


@tool
def sql_analytics(question: str) -> str:
    """Answer analytical questions by querying the <describe your data here,
    e.g. 'sales orders, customers, and inventory'> database.

    Use for aggregations, counts, trends, and lookups. Input should be a
    complete natural-language question, e.g. 'Total revenue per month in 2025'.
    """
    try:
        result = _get_sql_agent().invoke({"messages": [("user", question)]})
        return result["messages"][-1].content
    except Exception as e:
        return f"SQL analytics failed: {e}"