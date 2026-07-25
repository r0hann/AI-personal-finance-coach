# /dev

Build a new feature or change in this project.

Sources:
- awesome-prompts/agentic_coder.txt (plan-first, security checklist)
- langgptai/awesome-claude-prompts Smart Dev (DB compat checks, module deps)
- hesreallyhim/awesome-claude-code Agent Collab Skills (acceptance gate)
- promptslab/Awesome-Prompt-Engineering (spec-first, Pydantic validation)

## When invoked
Follow this spec-first workflow. Plan before touching any file.

---

### Phase 1 — Read before writing

1. Read the relevant router in `backend/routers/`
2. Read the relevant service in `backend/services/`
3. Check `supabase/schema.sql` if the feature touches the DB
4. Check `.claude/rules/mistakes.md` for known pitfalls
5. Check `ai-providers.md` if the feature needs an AI call

Ask:
- Does this need a new DB table or does the existing schema cover it?
- Does this need a new AI call or can it reuse `complete()` / `stream()`?
- Which provider should handle it and why?
- What existing code could break?

---

### Phase 2 — Write a spec (state this before any code)

```
Feature: [name]
Files to change: [list]
New files needed: [list or none]
DB changes: [yes/no — describe if yes]
AI provider: [which one + why]
Pydantic model needed: [yes/no]
Risk: [what could break]
Acceptance criteria: [how we know it works]
```

If spec has gaps → resolve them before coding.

---

### Phase 3 — Build in this order

1. **DB** — add migration to `supabase/schema.sql` if needed
2. **Pydantic model** — add to `backend/models/` with strict types, no `Any`
3. **Service** — add to `backend/services/`
   - AI: `from services.ai_provider import complete, stream`
   - DB: `from db.supabase import get_client` → `.execute().data`
4. **Router** — add endpoint to `backend/routers/`, register in `main.py`
5. **Frontend** — API call + component in `frontend/src/`
   - Use `import.meta.env.VITE_API_BASE_URL` — never hardcode localhost
   - Streaming: `fetch` + `response.body.getReader()` — not axios

---

### Phase 4 — DB compatibility checks (from Smart Dev)

Before any DB change, verify:
- [ ] New column has a default value or is nullable (no NOT NULL without default on existing table)
- [ ] Foreign keys reference existing tables in `schema.sql`
- [ ] New indexes don't duplicate existing ones (`transactions_date_idx`, `transactions_category_idx`)
- [ ] Amount fields use `numeric(12,2)` — not `float` or `decimal`
- [ ] Date fields use `date` type — not `timestamp` or `text`

---

### Phase 5 — Security checklist

- [ ] No API keys in code — all from `config.py` env vars
- [ ] All user input validated by Pydantic before DB or AI
- [ ] No raw SQL — use Supabase query builder only
- [ ] No hardcoded URLs in frontend
- [ ] Streaming endpoints have no unbounded loops

---

### Phase 6 — Acceptance gate

Before marking done, verify each criterion from the spec:
- Hit the endpoint manually (curl or frontend)
- Check logs for which AI provider was actually used
- Check DB rows in Supabase dashboard
- Confirm fallback still works: pass a bad API key, verify next provider kicks in

---

## Project shortcuts

| What you want | Where it goes |
|---------------|---------------|
| New AI feature | `backend/services/` → `ai_provider.complete()` |
| New endpoint | `backend/routers/` → register in `main.py` |
| New data type | `backend/models/` → `supabase/schema.sql` |
| New chart | `frontend/src/` → Recharts `ResponsiveContainer` |
| Improve chat | `backend/services/gemini_chat.py` `_SYSTEM` prompt |
| New insight | `backend/services/ai_coach.py` `_INSIGHTS_SYSTEM` |
| New provider | Use `/add-provider` skill first |

## Rules
- Spec before code — never start with "let me just edit the file"
- One feature per session — easier to review and revert
- If something breaks mid-build → use `/debug` before guessing
- Record outcome when done: did it work first try or need fixes?
