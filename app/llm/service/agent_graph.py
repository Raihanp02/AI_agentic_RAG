from typing_extensions import Literal
from langchain_core.messages import SystemMessage, HumanMessage, RemoveMessage

from langgraph.graph import START, END
from langgraph.graph import MessagesState, StateGraph
from langgraph.prebuilt import ToolNode

from app.llm.service.agent_tools.rag_tools import rag_tools
from app.llm.service.llm import OpenRouterLLM
from core.config import settings

class States(MessagesState):
    summary: str

class AgenticRAGGraph:
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

        async def assistant(self, state: States):
            summary = state.get("summary", "")

            if summary:
                message = [SystemMessage(content=f"Summary of the conversation so far: {summary}")] + state.get("messages")

            else:
                message = state.get("messages")

            response = await self.llm.ainvoke(message)

            return {"messages": [response]}
        
        async def summarize(self, state: States):
            summary = state.get("summary", "")

            if summary:
                summary_message = f"Summary of the conversation so far: {summary} please extend it with messages above."
            else:
                summary_message = "Please summarize the conversation so far."

            message = state.get("messages") + [HumanMessage(content=summary_message)]

            response = await self.llm.ainvoke(message)

            return {"summary": response.content, "messages": [RemoveMessage(id=m.id) for m in state["messages"][:-2]]}
        
        # conditional edge
        def conditional_edge(self, state: States):
            last_message = state["messages"][-1]

            if last_message.tool_calls:
                return "tools"
            if len(state.get("messages", [])) > 6:
                return "summarize"
            else:
                return END
                
        def build_graph(self, parent):
            self._add_node(parent)
            self._add_edges()

            graph = self.graph.compile()
            return graph
        
        def _add_node(self, parent):
            self.graph.add_node("assistant", self.assistant)
            self.graph.add_node("summarize", self.summarize)
            self.graph.add_node("tools", ToolNode(parent.tools))

        def _add_edges(self):
            self.graph.add_edge(START, "assistant")
            self.graph.add_conditional_edges(
                "assistant", 
                self.conditional_edge, 
                {
                    "tools": "tools",
                    "summarize": "summarize",
                    END: END,
                })
            self.graph.add_edge("summarize", END)
            self.graph.add_edge("tools", "assistant")

chat_graph = AgenticRAGGraph(llm_method=OpenRouterLLM(), tools=[rag_tools])