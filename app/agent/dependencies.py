from fastapi import Request

from app.agent.service.graph.agent_graph import AgenticRAGGraph  # wherever the class lives


def get_graph(request: Request) -> AgenticRAGGraph:
    return request.app.state.chat_graph