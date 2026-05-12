# Agentic RAG

This repository implements an agentic retrieval-augmented generation (RAG) service using FastAPI, LangChain, and LangGraph.

## What this repo contains

- `app/main.py`: FastAPI application entrypoint
- `app/knowledge/`: knowledge ingestion, chunking, embedding, and storage
- `app/llm/`: LLM agent graph, chat endpoint, and tool integration
- `core/`: configuration and shared state management
- `migrations/`: database migration history

## Documentation

The documentation architecture is under `docs/`:

- `docs/getting_started.md`: install, environment, run instructions
- `docs/architecture.md`: system and component architecture
- `docs/api.md`: endpoint reference for `/api`
- `docs/development.md`: development workflows and extension points

## Quick start

1. Copy `.env.example` to `.env`
2. Set `DATABASE_ASYNC_URL`, `DATABASE_SYNC_URL`, `OPENROUTER_API_KEY`, `OPENROUTER_BASE_URL`, and `OPENROUTER_MODEL`
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the app:
   ```bash
   uvicorn app.main:app --reload
   ```

## Recommended reading

Start with `docs/getting_started.md`, then read `docs/architecture.md` for the overall design and `docs/api.md` for available endpoints.
