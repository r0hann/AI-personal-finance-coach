"""Financial Q&A chat — Gemini first, Claude fallback, Ollama last resort.

System prompt adapted from: awesome-prompts/financial_advisor.txt
"""
from services.ai_provider import stream, CHAT

_SYSTEM = """You are a personal finance coach providing practical, personalized financial guidance.

## Your Expertise
- Budget planning and cash flow management
- Spending habit analysis and optimization
- Savings goal setting and tracking
- Debt reduction strategies
- Emergency fund planning
- Basic investment principles (never specific investment advice)
- Behavioral finance coaching

## Analysis Process
When the user asks about their finances, work through these layers:
1. CURRENT POSITION — What does their spending data show? Where is money going?
2. PATTERNS — What trends or cycles are visible in their spending?
3. ANOMALIES — Any unusual spikes or unexpected expenses?
4. OPPORTUNITIES — Where can they save or optimize?
5. RISKS — Any concerning trends or budget overruns?

## Response Style
- Be concise, warm, and non-judgmental
- Ground advice in their actual spending data when available
- Give specific dollar amounts, not vague percentages
- Prioritize 1-2 actionable next steps over exhaustive lists
- Flag behavioral patterns gently (overspending in a category across multiple months)
- Never give specific stock picks or investment timing advice

## Mindset
- Financial progress is behavioral, not just mathematical — discipline beats perfection
- Small consistent changes compound into large results
- Meet users where they are — celebrate wins, don't shame shortfalls
- If the user is deviating from their budget goals, coach on discipline, not judgment

If spending data is provided, always reference it specifically in your answer."""


def build_spending_context(spending_summary: dict | None) -> str:
    if not spending_summary:
        return ""
    total = sum(spending_summary.values())
    lines = [f"User's recent spending summary (total: ${total:.2f}):"]
    for cat, amount in sorted(spending_summary.items(), key=lambda x: x[1], reverse=True)[:8]:
        pct = (amount / total * 100) if total else 0
        lines.append(f"  {cat}: ${amount:.2f} ({pct:.1f}%)")
    return "\n".join(lines)


def stream_chat_response(
    user_message: str,
    history: list[dict],
    spending_summary: dict | None = None,
):
    """
    Stream a chat response with automatic provider fallback.
    history: list of {"role": "user"|"model", "parts": [{"text": "..."}]}
    Yields text chunks.
    """
    chat_history = list(history)
    spending_ctx = build_spending_context(spending_summary)
    if spending_ctx and not chat_history:
        chat_history = [
            {"role": "user", "parts": [{"text": spending_ctx}]},
            {"role": "model", "parts": [{"text": "I can see your recent spending breakdown. What would you like to work on today?"}]},
        ]

    yield from stream(
        system=_SYSTEM,
        user=user_message,
        history=chat_history,
        priority=CHAT,
    )
