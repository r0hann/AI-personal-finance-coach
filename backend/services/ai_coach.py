"""Claude Haiku service for insights, savings suggestions, and budget forecasting."""
import json
import re
import anthropic
from datetime import datetime
from config import settings

_client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

_INSIGHTS_SYSTEM = """You are a personal finance coach. Analyze spending data and return structured JSON insights.
Always return valid JSON with this exact structure:
{
  "summary": "One sentence overview of spending this month",
  "insights": [
    {"title": "...", "description": "...", "type": "warning|info|success"}
  ],
  "savings_suggestions": [
    {"category": "...", "suggestion": "...", "estimated_savings": 0.0}
  ]
}
Keep insights specific, actionable, and non-judgmental."""


def generate_monthly_insights(month_year: str, spending_by_category: dict, prev_month: dict | None = None) -> dict:
    """Generate AI insights for a given month's spending breakdown."""
    context = f"Month: {month_year}\nSpending by category:\n"
    for cat, amount in sorted(spending_by_category.items(), key=lambda x: x[1], reverse=True):
        context += f"  {cat}: ${amount:.2f}\n"

    if prev_month:
        context += "\nPrevious month for comparison:\n"
        for cat, amount in prev_month.items():
            context += f"  {cat}: ${amount:.2f}\n"

    response = _client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        system=[{
            "type": "text",
            "text": _INSIGHTS_SYSTEM,
            "cache_control": {"type": "ephemeral"},
        }],
        messages=[{"role": "user", "content": context}],
    )

    text = response.content[0].text.strip()
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        return json.loads(match.group())

    return {
        "summary": "Unable to generate insights at this time.",
        "insights": [],
        "savings_suggestions": [],
    }


_FORECAST_SYSTEM = """You are a financial forecasting assistant. Given 3-month rolling average spending by category
and set budget limits, write a brief (2-3 sentence) forecast paragraph. Identify which categories are on track
and which may exceed budget. Be specific with dollar amounts. Return only the paragraph, no JSON."""


def generate_budget_forecast(rolling_averages: dict, budget_limits: dict) -> str:
    """Generate a narrative budget forecast paragraph using Claude."""
    context = "3-month rolling average spending:\n"
    for cat, avg in sorted(rolling_averages.items(), key=lambda x: x[1], reverse=True):
        limit = budget_limits.get(cat)
        if limit:
            pct = (avg / limit) * 100
            context += f"  {cat}: ${avg:.2f}/mo (budget: ${limit:.2f}, {pct:.0f}% used)\n"
        else:
            context += f"  {cat}: ${avg:.2f}/mo (no budget set)\n"

    response = _client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=256,
        system=[{
            "type": "text",
            "text": _FORECAST_SYSTEM,
            "cache_control": {"type": "ephemeral"},
        }],
        messages=[{"role": "user", "content": context}],
    )

    return response.content[0].text.strip()
