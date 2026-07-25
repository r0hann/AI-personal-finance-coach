---
paths:
  - "shared_memory/**/*.py"
---

# Shared Memory Rules

## Purpose
Cross-session, cross-provider memory for multi-AI chat.
Stores chat sessions so Claude, Gemini, and Ollama share context.

## Storage
- Sessions stored at `~/.ai-shared-memory/sessions/<YYYYMMDD_HHMMSS>.json`
- Global location — shared across all apps on the machine
- Never store sessions inside the project directory

## Session lifecycle
1. `start_session(providers, topic_hint)` — call when user opens chat, returns past context string
2. `add_message(role, content, provider)` — call after every message turn
3. `add_key_fact(fact)` — call when user states an important preference or goal
4. `end_session(summary)` — call when user closes chat

## Auto-cleanup rules (do not change)
- Sessions older than 7 days → deleted on next `start_session()`
- Sessions with fewer than 2 messages → deleted on `end_session()`
- Corrupted JSON files → deleted silently on next cleanup

## Relevance scoring
- Keyword overlap between `topic_hint` and past session text drives relevance
- Sessions from last 24h get +0.5 recency boost
- Top 3 relevant sessions are injected as context — never more
