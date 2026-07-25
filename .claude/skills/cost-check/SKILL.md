# /cost-check

Audit AI provider costs and token usage for this project.

Sources:
- awesome-prompts/agent_cost_observability_architect.txt (telemetry, anomaly detection)
- hesreallyhim/awesome-claude-code llm-router (cheapest capable model routing)
- promptslab/Awesome-Prompt-Engineering (prompt caching = 90% cost reduction)

## When invoked
Run a full cost audit. Report burn rate, flag anomalies, recommend optimizations.

---

### Step 1 — Verify prompt caching is active (biggest lever: up to 90% reduction)

Check `backend/services/ai_provider.py` `_complete_claude()`:
- System prompt block must have `"cache_control": {"type": "ephemeral"}`
- If missing → add it. This is the single highest-impact cost reduction.
- Cache hits show as `cache_read_input_tokens` in the Anthropic API response

Check `backend/services/ai_coach.py` and `categorizer.py`:
- Both pass system prompts through `ai_provider.complete()` — caching is inherited
- If system prompts changed recently → cache was invalidated, first call is expensive

---

### Step 2 — Current provider pricing

| Provider | Input | Output | Free tier |
|----------|-------|--------|-----------|
| Claude Haiku 4.5 | ~$0.80/M | ~$4/M | None |
| Gemini 2.5 Flash | ~$0.075/M | ~$0.30/M | 1,500 req/day |
| Ollama (local) | $0 | $0 | Unlimited |

Verify current prices at: console.anthropic.com and aistudio.google.com

---

### Step 3 — Estimate cost per 100 active users/day

| Feature | Provider | Est. tokens/user | Est. cost/100 users |
|---------|----------|-----------------|---------------------|
| Categorization | Gemini (free) | 700 in + 200 out | ~$0.00 (free tier) |
| Monthly insights | Claude | 800 in + 400 out | ~$0.24/month |
| Budget forecast | Claude | 400 in + 150 out | ~$0.09/month |
| Chat | Gemini (free) | 10K in + 3K out/session | ~$0.00 (free tier) |
| **Total/month** | | | **~$0.33/month** |

At scale (1,000 users): ~$3.30/month — still very cheap.

---

### Step 4 — Anomaly checklist

Flag these as problems:
- [ ] Categorization hitting Claude instead of Gemini → Gemini rate limit exceeded, check logs
- [ ] `ProviderUnavailable` warnings in logs more than 1-2/day → quota issue
- [ ] Chat falling back to Claude → Gemini free tier exhausted (>1,500 req/day)
- [ ] Ollama being used in production → both paid providers down, investigate
- [ ] Insights being regenerated every page load → `insights_cache` table not being hit
- [ ] Unusually long prompts → spending context injected when not needed

---

### Step 5 — Optimization priority order

Apply highest-impact first:

1. **Prompt caching** (up to 90% Claude cost reduction) — verify `cache_control` is set
2. **Keyword rules before AI** — `_KEYWORD_RULES` in `categorizer.py` handles ~40% of transactions free
3. **Insights cache** — `insights_cache` table in Supabase caches monthly insights; verify it's used
4. **Route to cheapest capable model** — for simple categorization, Gemini Flash beats Claude on cost
5. **Batch size** — 50 transactions per Claude call is optimal; don't reduce
6. **Ollama opt-in for privacy users** — zero cost for users who install it locally

---

### Step 6 — Report output

```
AI Cost Audit — [date]

Prompt caching: [active / MISSING — fix immediately]

Estimated cost (100 active users):
  Categorization: $X.XX  (provider: gemini/claude)
  Insights:       $X.XX  (provider: claude/gemini, cached: yes/no)
  Forecast:       $X.XX  (provider: claude/gemini)
  Chat:           $X.XX  (provider: gemini/claude)
  TOTAL/month:    $X.XX

Anomalies: [none | list]
#1 optimization: [single highest-impact action]
```
