---
paths:
  - "backend/**/*.py"
---

# Backend Rules (Python / FastAPI)

## Stack
- Python 3.11, FastAPI, uvicorn, Supabase (hosted Postgres)
- All routes live in `backend/routers/`, services in `backend/services/`
- DB access only via `from db.supabase import get_client` — never instantiate Supabase client directly

## FastAPI conventions
- Use `APIRouter` with `prefix` and `tags` in every router file
- Return plain dicts or Pydantic models — never raw strings except StreamingResponse
- Streaming responses use `StreamingResponse(generate(), media_type="text/plain")`
- Pydantic models go in `backend/models/` — one file per domain

## Supabase patterns
- Always chain `.execute().data` — never use `.execute()` result directly
- Expenses are negative amounts (`amount < 0`) — income is positive
- Date format is ISO string (`date.isoformat()`) for all queries

## AI provider rules
- Never import `anthropic` or `google.generativeai` directly in routers or models
- All AI calls go through `from services.ai_provider import complete, stream`
- Provider priority chains are defined in `ai_provider.py` — do not hardcode providers elsewhere
- Catch `ProviderUnavailable` not raw SDK errors
- Always use `cache_control: {"type": "ephemeral"}` on Claude system prompts

## Error handling
- Let FastAPI handle 422 validation errors automatically
- Only catch errors at system boundaries (external APIs, DB calls)
- AI provider failures fall through the chain — no manual retry logic needed
