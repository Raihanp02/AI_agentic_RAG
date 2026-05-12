# API Reference

This service exposes two main API domains: knowledge ingestion and chat.

## Base path

All endpoints are mounted under `/api`.

## Knowledge endpoints

### `POST /api/insert-knowledge`

Upload one or more documents for ingest, chunking, embedding, and storage.

Request:
- `source`: multipart file list
- `category` (optional): string

Response:
- `message`: status message
- `job_ids`: array of job IDs for progress tracking

### `GET /api/progresses`

Returns the current processing progress for ingest jobs.

Response:
- JSON object keyed by job ID with status metadata

## Chat endpoint

### `POST /api/chat`

Send a user message to the LLM agent graph.

Request body:
- `messages`: string

Response:
- The raw graph execution result from `langgraph`

### Example

```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"messages": "Hello world"}'
```

## Error handling

- `500` on internal graph or ingestion failures
- FastAPI will return validation errors for malformed requests

## Notes

- The `/api/insert-knowledge` endpoint uses a background `ProcessPoolExecutor` and returns immediately with job IDs.
- Progress is tracked in a multiprocessing-safe `progress_dict` stored in `core/state.py`.
