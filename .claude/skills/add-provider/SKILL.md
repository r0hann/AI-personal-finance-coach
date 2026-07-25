# /add-provider

Add a new AI provider to the fallback chain or assign a new vendor to a feature.

## When invoked
Follow these steps to add or reassign a provider without breaking existing fallbacks.

### Step 1 — Justify the addition
Answer before writing any code:
- What does this provider do better than the current primary? (specific benchmark or reason)
- What are its known failure modes for this task?
- Does adding it create vendor monoculture in any feature? (two providers from same company = risk)

### Step 2 — Map the role
Assign based on complementary strengths, not convenience:

| Provider | Best for in this project |
|----------|--------------------------|
| Claude Haiku | Structured JSON output, prompt caching, batch tasks |
| Gemini Flash | Streaming chat, large context, free tier volume |
| Ollama (local) | Privacy-sensitive data, offline fallback, zero cost |
| New provider | Define clearly before adding |

### Step 3 — Update `ai_provider.py`
1. Add a `_complete_<provider>()` function following the existing pattern
2. Add a `_stream_<provider>()` function if it supports chat
3. Add to `_COMPLETE` and `_STREAM` dicts
4. Catch rate-limit/quota errors and raise `ProviderUnavailable`
5. Add to the relevant priority chain constant (`CATEGORIZATION`, `INSIGHTS`, `FORECAST`, `CHAT`)

### Step 4 — Update `config.py`
- Add API key or base URL as Optional[str] with a sensible default
- Add to `.env.example` with a comment explaining where to get it

### Step 5 — Test the fallback chain
- Verify the new provider works as primary
- Simulate rate limit (pass a bad API key) and confirm fallback to next provider
- Confirm Ollama still works as last resort

### Step 6 — Document in `.claude/rules/ai-providers.md`
- Add the provider to the priority table
- Document its rate limits and known failure modes
- Note if it changes cost structure (free tier vs. paid)

## Rules
- Never add a provider without documenting its failure modes first
- Never create monoculture: don't use two providers from the same company in the same fallback chain
- Provider divergence (two providers giving different answers) is a signal worth logging, not hiding
- Keep Ollama as last resort in every chain — it's the zero-cost offline escape hatch
