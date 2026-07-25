# /debug

Systematic bug investigation for this project.

Sources:
- awesome-prompts/debugging_agent.txt (7-stage methodology)
- hesreallyhim/awesome-claude-code (ReAct pattern, outcome telemetry)
- promptslab/Awesome-Prompt-Engineering (ReAct: reason→act→observe loop)

## When invoked
Run through these stages in order. Never skip. Never guess.
Every claim must be grounded in actual code or output.

---

### ReAct Loop (run this before the 7 stages for fast bugs)
For simple bugs, cycle through this first:
1. **REASON** — what do I expect vs. what is happening?
2. **ACT** — read one file or check one log
3. **OBSERVE** — what did I actually find?
4. Repeat until cause is pinned. Then fix.

If 3 ReAct cycles don't localize it → escalate to full 7-stage below.

---

### Full 7-Stage Investigation

**1. REPRODUCE**
- Confirm the symptom is consistent and repeatable
- Ask: "When did this start? Has it ever worked?"
- Get exact error message, stack trace, or wrong output

**2. OBSERVE**
- Read the full error — trust it, don't dismiss it
- Check logs: `uvicorn` stdout, browser console, Supabase dashboard
- Read before mutating — never change code before reading relevant files

**3. HYPOTHESIZE**
- Form 2-4 testable candidates ranked by likelihood
- State each as: "IF [cause] THEN [symptom] BECAUSE [mechanism]"
- Common suspects in this project:
  - Missing `.execute().data` on Supabase call
  - AI provider rate limit (look for 429 / "quota" / "resource exhausted")
  - `amount > 0` when expenses are NEGATIVE in this schema
  - Hardcoded `localhost:8000` instead of `VITE_API_BASE_URL`
  - `docker-compose` (hyphen) vs `docker compose` (space)
  - Prompt cache miss → Claude system prompt not getting `cache_control`
  - Provider fallback silently swallowing an error instead of raising

**4. TEST**
- One change at a time — multiple changes make causation unclear
- Smallest test first: `print()` / `console.log()` before any fix
- For AI provider bugs: log the `provider_used` return value from `complete()`
- For DB bugs: print the raw `.execute()` response before `.data`

**5. LOCALIZE**
- Pin to specific file, function, and line range
- `backend/services/ai_provider.py` → provider errors
- `backend/db/supabase.py` → DB connection errors
- `backend/routers/` → request/response shape mismatches
- `shared_memory/manager.py` → session file corruption or missing cleanup

**6. FIX**
- Fix root cause, not symptom
- One fix per commit — don't bundle unrelated changes
- After fixing: verify provider fallback chain still works end-to-end

**7. EXPLAIN + RECORD**
- State WHY the bug existed (not just what you changed)
- If it's a repeatable pattern → add to `.claude/rules/mistakes.md`
- Note the outcome: "fix worked / fix reverted" so future sessions learn from it

---

## Tracing tools (for hard bugs)
- Add `import logging; log = logging.getLogger(__name__)` to the failing service
- Log `provider_used` after every `complete()` / `stream()` call
- For DB: enable Supabase query logging in dashboard → Settings → Logs

## Rules
- Never run mutations before reading relevant files
- For intermittent bugs: get a minimal reproduction case first
- If a fix is reverted, record WHY — reverts are more informative than fixes
