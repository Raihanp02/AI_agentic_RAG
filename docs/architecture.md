# System Architecture

This document describes the major components of the repository and how they work together.

## High-level architecture

The repository is a FastAPI application with two main domains:

1. Knowledge ingestion and storage
2. LLM agent chat using LangGraph

The app coordinates document upload, parsing, chunking, embedding, and storage in PostgreSQL, while the chat endpoint uses a stateful graph agent with optional tool calls.

## Component map

### `app/main.py`
- Entrypoint for the FastAPI app
- Sets up database checkpointing for LangGraph
- Mounts `app.llm.routers` and `app.knowledge.routers`

### `core/config.py`
- Loads environment variables via `pydantic-settings`
- Provides `DATABASE_ASYNC_URL`, `DATABASE_SYNC_URL`, and OpenRouter settings

### `app/knowledge/api/knowledge.py`
- Defines knowledge ingestion endpoints
- Starts ingestion jobs in a background `ProcessPoolExecutor`
- Exposes progress tracking

### `app/knowledge/service/add_knowledge`
- `DoclingParser`: parses uploaded documents and extracts markdown/text
- `DoclingHybridChunker`: splits parsed text into chunks
- `HuggingFaceTextEmbedder`: creates vector embeddings for chunks
- `KnowledgePipeline`: orchestrates parsing, chunking, embedding, and storage

### `app/knowledge/service/crud_knowledge`
- `store.py`: stores documents and embeddings in PostgreSQL
- `retrieve.py`: retrieves vector search results (future use)

### `app/knowledge/database`
- `session.py`: defines both async and sync SQLAlchemy session factories
- `models/`: database models for documents, chunks, and vector storage

### `app/llm/api/agent.py`
- Defines the `/api/chat` endpoint
- Sends user messages into the LangGraph state graph

### `app/llm/service/agent_graph.py`
- Builds the agent graph with states and conditional edges
- Uses tools via `ToolNode`
- Summarizes the conversation if it grows too long

### `app/llm/service/llm.py`
- Wraps LangChain OpenAI/OpenRouter model configuration
- Provides a consistent LLM interface for the graph

### `app/llm/service/agent_tools/rag_tools.py`
- Defines RAG tools available to the agent
- These tools can be used during graph execution

### `core/state.py`
- Holds `progress_dict` in a multiprocessing-safe manager
- Tracks progress for ingestion jobs across processes

## Data flow

1. User uploads document(s) to `/api/insert-knowledge`
2. `KnowledgePipeline.process_document` runs in a worker process
3. Document is parsed, chunked, and embedded
4. Metadata and vector embeddings are persisted to Postgres
5. Progress state updates are written to `progress_dict`

For chat:

1. User sends a message to `/api/chat`
2. `chat_graph.graph.ainvoke` runs the LangGraph state graph
3. Graph may call tools or summarize conversation state
4. Response is returned to the user

## Deployment notes

- `DATABASE_ASYNC_URL` and `DATABASE_SYNC_URL` both need valid DB connection strings
- Postgres must support `pgvector`
- The app uses `uvicorn` for local development and FastAPI for API docs

## Extension points

- Add new ingestion parsers or chunkers under `app/knowledge/service/add_knowledge`
- Add new tools in `app/llm/service/agent_tools`
- Extend database schemas in `app/knowledge/database/models`
- Add API endpoints in `app/knowledge/api` or `app/llm/api`
