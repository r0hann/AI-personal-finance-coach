# Known Mistakes & Patterns to Avoid

Sources: project experience + awesome-prompts + langgptai + promptslab research

---

## AI / Providers
- NEVER import `anthropic` or `google.generativeai` directly in routers or models
  → Always use `from services.ai_provider import complete, stream`
- NEVER hardcode a provider in a service — use priority chain constants from `ai_provider.py`
- NEVER use `claude-haiku-4-5` (without date suffix) — correct: `claude-haiku-4-5-20251001`
- NEVER omit `cache_control: {"type": "ephemeral"}` on Claude system prompts — costs up to 90% more
- NEVER swallow a `ProviderUnavailable` silently — log it so fallback chain is visible in logs
- NEVER assume Gemini is free forever — check free tier limit (1,500 req/day) before adding features

## Database
- NEVER forget `.execute().data` — `.execute()` alone returns a response object, not rows
- NEVER query expenses with `amount > 0` — expenses are NEGATIVE in this schema
- NEVER instantiate Supabase client directly — always use `get_client()` from `db/supabase.py`
- NEVER add a NOT NULL column to an existing table without a DEFAULT value
- NEVER use `float` for money — always `numeric(12,2)` in schema and Python

## Pydantic / Validation
- NEVER use `Any` type in Pydantic models — define explicit types
- NEVER skip Pydantic validation on user input before passing to DB or AI
- NEVER return raw Supabase rows to the frontend — map to a Pydantic response model first

## Frontend
- NEVER hardcode `http://localhost:8000` — use `import.meta.env.VITE_API_BASE_URL`
- NEVER use axios for streaming chat — use `fetch` with `response.body.getReader()`
- NEVER use `any` type in TypeScript — define explicit API response types
- NEVER render charts without `ResponsiveContainer` — they will break on mobile

## Shared Memory
- NEVER store session files inside the project directory
- NEVER call `end_session()` without calling `start_session()` first
- NEVER skip `add_message()` — both user and assistant turns must be logged

## Docker
- Use `docker compose` (space) — `docker-compose` (hyphen) is v1 and not installed
- `.env` file must exist before `docker compose up` — copy from `.env.example` first

## General Coding
- NEVER add comments explaining WHAT code does — only WHY (non-obvious constraints/decisions)
- NEVER create new files when editing an existing one works
- NEVER bundle unrelated changes in one commit — one fix / one feature per commit
- NEVER guess at a bug fix — read the error and the relevant file first (ReAct: reason→act→observe)
- When a fix is reverted, record WHY in this file — reverts reveal more than fixes do
