from core.database.session import get_db
from app.llm.service.llm import OpenRouterLLM
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langchain.agents import create_react_agent

from core.config import settings

class QueryTools:
    def __init__(self, db_uri, llm=OpenRouterLLM()):
        self.db = SQLDatabase.from_uri(db_uri)
        self.llm = llm
        self.toolkit = SQLDatabaseToolkit(db=self.db, llm=self.llm)
        self.tools = self.toolkit.get_tools()
        self.sql_agent = create_react_agent(
            model=self.llm,
            tools=self.tools
        )

db_uri = (
    f"{settings.DATABASE_SYNC_URL}"
    f"?options=-csearch_path%3D{settings.QUERY_SCHEMA_NAME}"
)
llm = ChatOpenAI(model="gpt-4.1")

query_tool = QueryTools(db_uri, llm)

@tool
def sql_analytics(question: str) -> str:
    """Answer analytical questions using the SQL database."""
    
    result = query_tool.sql_agent.invoke({
        "messages": [
            ("user", question)
        ]
    })

    return result["messages"][-1].content