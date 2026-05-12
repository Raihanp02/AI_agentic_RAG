# Getting Started

## Prerequisites

- Python 3.11+ recommended
- PostgreSQL database with `pgvector` extension enabled
- OpenRouter API key (or equivalent OpenAI-compatible provider)

## Installation

```bash
pip install -r requirements.txt
```

## Environment configuration

Copy the example environment file:

```bash
cp .env.example .env
```

Then update `.env` with your values:

```text
DATABASE_ASYNC_URL=postgresql+asyncpg://user:password@host:port/dbname
DATABASE_SYNC_URL=postgresql://user:password@host:port/dbname
OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_MODEL=gemini-2.0-pro
```

> Note: The code requires both `DATABASE_ASYNC_URL` and `DATABASE_SYNC_URL`.

## Run locally

```bash
uvicorn app.main:app --reload
```

## Health check

Open `http://localhost:8000/docs` to view the FastAPI interactive API documentation.

## Database migrations

This project uses Alembic for migrations.

```bash
alembic upgrade head
```

If you add or modify models, generate a new revision:

```bash
alembic revision --autogenerate -m "describe change"
```
