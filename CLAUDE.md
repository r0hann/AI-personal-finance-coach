# AI Personal Finance Coach — Project Guide

## AI Provider Split

| Feature | Provider | Model | Reason |
|---------|----------|-------|--------|
| Transaction categorization | Claude | `claude-haiku-4-5-20251001` | Batch + prompt caching, cost-efficient |
| Monthly insights & savings | Claude | `claude-haiku-4-5-20251001` | Structured JSON output, cacheable |
| Budget forecasting narrative | Claude | `claude-haiku-4-5-20251001` | Short structured output |
| Financial Q&A chat | Gemini | `gemini-2.5-flash` | Large context, conversational streaming |

## Claude SDK Rules (enforced by `/claude-api` skill)
- Always use `cache_control: {"type": "ephemeral"}` on system prompts
- Use `stream=True` for any response that may be long
- Model string: `claude-haiku-4-5-20251001` (exact — no date suffix on the alias)
- Categorization: batch 50 transactions per call, cache the system prompt

## Gemini SDK Rules
- Use `google-generativeai` Python SDK
- Model: `gemini-2.5-flash`
- Always stream responses for chat
- Include last 3 months spending summary in system instruction (cached)

## Stack
- Backend: Python 3.11 + FastAPI + uvicorn
- Frontend: React + TypeScript + Tailwind CSS + Recharts
- Database: Supabase (hosted Postgres)
- Data import: CSV via pandas

## Environment Variables
```
ANTHROPIC_API_KEY=
GOOGLE_API_KEY=
SUPABASE_URL=
SUPABASE_SERVICE_KEY=
VITE_API_BASE_URL=http://localhost:8000
```

## Running Locally
```bash
# Backend
cd backend && pip install -r requirements.txt
uvicorn main:app --reload

# Frontend
cd frontend && npm install
npm run dev
```
