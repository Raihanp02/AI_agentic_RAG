from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, RemoveMessage, SystemMessage
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition


class States(MessagesState):
    summary: str


class AgenticRAGGraph:
    def __init__(self, llm: BaseChatModel, tools: list, checkpointer=None):
        self.llm = llm
        self.llm_with_tools = llm.bind_tools(tools)
        self.tools = tools
        self.graph = self._build(checkpointer)

    async def assistant(self, state: States):
        messages = state["messages"]
        if summary := state.get("summary"):
            messages = [SystemMessage(content=f"Summary of the conversation so far: {summary}")] + messages
        response = await self.llm_with_tools.ainvoke(messages)
        return {"messages": [response]}

    async def summarize(self, state: States):
        messages = state["messages"]
        summary = state.get("summary", "")
        prompt = (
            f"Summary so far: {summary}\n\nExtend it with the conversation above."
            if summary
            else "Summarize the conversation above."
        )
        response = await self.llm.ainvoke(messages + [HumanMessage(content=prompt)])

        # keep the last user turn onward; never split a tool-call/tool-result pair
        last_human = max(i for i, m in enumerate(messages) if isinstance(m, HumanMessage))
        return {
            "summary": response.content,
            "messages": [RemoveMessage(id=m.id) for m in messages[:last_human]],
        }

    def route(self, state: States):
        if tools_condition(state) == "tools":
            return "tools"
        return "summarize" if len(state["messages"]) > 6 else END

    def _build(self, checkpointer):
        g = StateGraph(States)
        g.add_node("assistant", self.assistant)
        g.add_node("tools", ToolNode(self.tools))
        g.add_node("summarize", self.summarize)

        g.add_edge(START, "assistant")
        g.add_conditional_edges("assistant", self.route, ["tools", "summarize", END])
        g.add_edge("tools", "assistant")
        g.add_edge("summarize", END)
        return g.compile(checkpointer=checkpointer)