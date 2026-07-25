---
paths:
  - "backend/services/ai_provider.py"
  - "backend/services/categorizer.py"
  - "backend/services/ai_coach.py"
  - "backend/services/gemini_chat.py"
---

# AI Provider Rules

## Provider priority (do not change without discussion)
| Feature        | Primary  | Fallback 1 | Fallback 2 |
|----------------|----------|------------|------------|
| Categorization | Gemini   | Claude     | Ollama     |
| Insights       | Claude   | Gemini     | Ollama     |
| Forecast       | Claude   | Gemini     | Ollama     |
| Chat           | Gemini   | Claude     | Ollama     |

## Adding a new AI feature
1. Define the system prompt as a module-level constant (`_SYSTEM_*`)
2. Choose the priority chain from `ai_provider.py` constants
3. Call `complete()` for batch tasks, `stream()` for chat
4. Never call Claude/Gemini/Ollama SDKs directly from service files

## Prompt standards (from awesome-prompts)
- Chat prompts follow the Financial Advisor framework (position → patterns → anomalies → opportunities → risks)
- Insights prompts follow the 6-layer Data Analysis framework
- Always include specific dollar amounts in AI instructions — not just percentages
- System prompts must include output format specification (JSON schema or paragraph)

## Claude-specific
- Model: `claude-haiku-4-5-20251001` (exact string — no aliases)
- Always set `cache_control: {"type": "ephemeral"}` on system prompt blocks
- Max tokens: 1024 for insights/categorization, 300 for forecast, 256 for short outputs

## Gemini-specific
- Model: `gemini-2.5-flash`
- Free tier limit: ~1500 req/day — Gemini is primary to maximize free usage
- Rate limit errors contain "quota", "429", or "resource exhausted" in message

## Ollama (local fallback)
- Requires Ollama running at `OLLAMA_BASE_URL` (default: http://localhost:11434)
- Default model: `llama3.2` — configurable via `OLLAMA_MODEL` env var
- Connection errors mean Ollama isn't running — log warning, don't crash

## Cost optimization (from promptslab/Awesome-Prompt-Engineering)
- Prompt caching reduces Claude costs up to 90% — always verify `cache_control` is set
- Route to cheapest capable model first (Gemini free tier → Claude paid → Ollama free)
- Use `/cost-check` skill to audit spend before adding any new AI feature

## Guardrails (from hesreallyhim/awesome-claude-code GouvernAI pattern)
- Auto-approve: read-only DB queries, keyword categorization, cached insight lookups
- Gate (log + warn): AI calls over 1024 tokens, provider fallback activations
- Block: any AI call with raw user input not validated by Pydantic first

## Future providers to consider
- **OpenRouter** — unified API across 300+ models, useful if adding more providers
- **DSPy (Stanford)** — systematic prompt optimization across providers, useful for tuning categorization accuracy
- Do NOT add new providers without using `/add-provider` skill first
