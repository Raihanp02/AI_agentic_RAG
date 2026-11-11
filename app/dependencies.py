from knowledge.service.progress_service.store import get_progress_store
from fastapi import Request
from knowledge.service.progress_service.job_runner import IngestionJobRunner
from app.agent.service.graph.agent_graph import AgenticRAGGraph  # wherever the class lives


def get_graph(request: Request) -> AgenticRAGGraph:
    return request.app.state.chat_graph


def get_job_runner(request: Request) -> IngestionJobRunner:
    return request.app.state.job_runner