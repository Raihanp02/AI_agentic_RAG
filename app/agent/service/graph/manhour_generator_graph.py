from langgraph.graph import START, END
from langgraph.graph import MessagesState, StateGraph
from langgraph.prebuilt import ToolNode

from app.agent.service.agent_tools.rag_tools import rag_tools
from app.provider.llm import OpenRouterLLM
from core.config import settings
from typing import TypedDict, Optional, Literal
from pydantic import BaseModel, Field

# ---- Structured sub-models (also useful as tool schemas for structured output) ----

class RoleHours(BaseModel):
    BE: float = 0
    FE: float = 0
    QA: float = 0
    # extend with other roles as needed, e.g. PM, DevOps, Design

class Feature(BaseModel):
    name: str
    description: Optional[str] = None
    roles: RoleHours


# ---- Graph State ----

class ManhourEstimationState(TypedDict):
    # --- input ---
    project_description: str
    features: Optional[list[Feature]] 
    output_path: Optional[str]            

class States(MessagesState):
    summary: str
    file_bytes: bytes

class MHGraph:
    def __init__(self, llm_method, tools: list, states = States):
        self.llm_method = llm_method
        self.tools = tools
        self.state = states
    
        self.nodes = self.Nodes(self)
        self.graph = self.nodes.build_graph(parent=self)

    def draw_graph(self):
        print(self.graph.get_graph().draw_mermaid())
        self.graph.get_graph().draw_png("graph.png")

    class Nodes:
        def __init__(self, parent):
            self.llm = parent.llm_method.llm.bind_tools(parent.tools)
            self.graph = StateGraph(parent.state)

        async def generate_manhour_estimation(self, state: ManhourEstimationState):
            
            return {
                "project_description": state["project_description"],
                "features": state.get("features", []),
                "output_path": state.get("output_path", None)
            }
    