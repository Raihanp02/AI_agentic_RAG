from typing_extensions import Literal
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, RemoveMessage

from langgraph.graph import END
from langgraph.graph import MessagesState, StateGraph
from langgraph.prebuilt import ToolNode


class States(MessagesState):
    summary: str

class AgenticRAGGraph:
    def __init__(self, llm: ChatOpenAI, tools: list, states = States()):
        self.llm = llm
        self.tools = tools
        self.state = states

        self.graph = self.Nodes().build_graph()

    class Nodes:
        def __init__(self):
            self.llm = AgenticRAGGraph.llm
            self.graph = StateGraph(AgenticRAGGraph.state)

        def assistant(self, state: MessagesState):
            summary = state.get("summary", "")

            if summary:
                message = [SystemMessage(content=f"Summary of the conversation so far: {summary}")] + state.get("messages")

            else:
                message = state.get("messages")

            response = self.llm.invoke(message)

            return {"messages": response}
        
        def summarize(self, state: MessagesState):
            summary = state.get("summary", "")

            if summary:
                summary_message = f"Summary of the conversation so far: {summary} please extend it with messages above."
            else:
                summary_message = "Please summarize the conversation so far."

            message = state.get("messages") + [HumanMessage(content=summary_message)]

            response = self.llm.invoke(message)

            return {"summary": response.content, "messages": [RemoveMessage(id=m.id) for m in state["messages"][:-2]]}
        
        # conditional edge
        def conditional_edge(self, state: MessagesState):
            last_message = state["messages"][-1]

            if last_message.tool_calls:
                return "tools"
            else: 
                if len(state.get("messages", [])) > 6:
                    return "summarize"
                else:
                    return END
                
        def build_graph(self):
            self.graph.add_node("assistant", self.assistant)
            self.graph.add_node("summarize", self.summarize)
            self.graph.add_node("tools", ToolNode(AgenticRAGGraph.tools))

            self.graph.add_edge("assistant", "conditional_edge")
            self.graph.add_edge("summarize", END)
            self.graph.add_edge("tools", "assistant")
            graph = self.graph.compile()
            return graph

