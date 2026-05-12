# Development Guide

## Code organization

- `app/main.py`: FastAPI application startup and router registration
- `app/knowledge/`: knowledge ingestion and database persistence
- `app/llm/`: graph-based LLM agent and tool integration
- `core/`: shared configuration and runtime state

## Adding knowledge ingestion logic

1. Add or update a parser in `app/knowledge/service/add_knowledge/doc_parser.py`
2. Update chunking logic in `app/knowledge/service/add_knowledge/doc_chunker.py`
3. Update embedding logic in `app/knowledge/service/add_knowledge/chunk_embedder.py`
4. Keep pipeline orchestration in `app/knowledge/service/add_knowledge/pipeline.py`

## Adding a new tool

1. Add new tool definitions to `app/llm/service/agent_tools/rag_tools.py`
2. Add the tool to `chat_graph` in `app/llm/service/agent_graph.py`
3. Update any docs or examples in `docs/api.md`

## Running tests

This repository does not include a dedicated tests folder yet. Recommended next steps:

- Add unit tests for `KnowledgePipeline`
- Add integration tests for `/api/insert-knowledge` and `/api/chat`
- Add database tests for `app/knowledge/database`

## Database migrations

- Use Alembic to manage schema changes
- The `migrations/` folder holds revision history
- Run `alembic upgrade head` after updating models

## Notes for contributors

- Keep API routes simple and move business logic into service modules
- Avoid blocking FastAPI with CPU-heavy work; the repository already uses `ProcessPoolExecutor` for ingestion
- Keep config in `core/config.py` and avoid hardcoding values in service modules
