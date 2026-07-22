"""Insights and budget forecasting — Claude first, Gemini fallback, Ollama last resort.

Insights prompt adapted from: awesome-prompts/data_analysis.txt
Forecast prompt adapted from: awesome-prompts/financial_advisor.txt
"""
import json
import re
from services.ai_provider import complete, INSIGHTS, FORECAST

_INSIGHTS_SYSTEM = """You are a personal finance data analyst. Analyze monthly spending data using this framework:

1. OVERVIEW — What does this month's spending represent overall?
2. PATTERNS — What trends or regularities are present vs. prior month?
3. ANOMALIES — What outliers, spikes, or unexpected values exist?
4. DRIVERS — What categories are causing the most spend or change?
5. OPPORTUNITIES — Where are the clearest savings opportunities?
6. RISKS — What concerning trends or budget overruns should be flagged?

Always return valid JSON with this exact structure:
{
  "summary": "2-3 sentence overview covering the most important finding from the analysis",
  "insights": [
    {
      "title": "Short finding title",
      "description": "Specific finding with dollar amounts. Reference actual data. Distinguish patterns from anomalies.",
      "type": "warning|info|success"
    }
  ],
  "savings_suggestions": [
    {
      "category": "Category name",
      "suggestion": "Concrete, specific action with expected outcome",
      "estimated_savings": 0.0
    }
  ]
}

Quality standards:
- Ground every claim in specific dollar amounts from the data
- Distinguish correlation from causation
- Flag data quality issues (e.g. missing categories, zero spend months)
- Limit to 4-6 insights and 2-4 savings suggestions — prioritize quality over quantity
- Use "warning" for overspending/risk, "success" for positive trends, "info" for neutral patterns"""


def generate_monthly_insights(month_year: str, spending_by_category: dict, prev_month: dict | None = None) -> dict:
    total = sum(spending_by_category.values())
    context = f"Month: {month_year}\nTotal spending: ${total:.2f}\nSpending by category:\n"
    for cat, amount in sorted(spending_by_category.items(), key=lambda x: x[1], reverse=True):
        pct = (amount / total * 100) if total else 0
        context += f"  {cat}: ${amount:.2f} ({pct:.1f}% of total)\n"

    if prev_month:
        prev_total = sum(prev_month.values())
        context += f"\nPrevious month comparison (total: ${prev_total:.2f}):\n"
        for cat, amount in sorted(prev_month.items(), key=lambda x: x[1], reverse=True):
            current = spending_by_category.get(cat, 0)
            change = current - amount
            sign = "+" if change >= 0 else ""
            context += f"  {cat}: ${amount:.2f} → ${current:.2f} ({sign}${change:.2f})\n"

    text, _ = complete(
        system=_INSIGHTS_SYSTEM,
        user=context,
        max_tokens=1024,
        priority=INSIGHTS,
    )

    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        return json.loads(match.group())

    return {"summary": "Unable to generate insights.", "insights": [], "savings_suggestions": []}


_FORECAST_SYSTEM = """You are a financial forecasting coach. Analyze 3-month rolling average spending against budget limits.

Write a 3-4 sentence forecast paragraph that covers:
1. OVERALL STATUS — Is the user broadly on track or at risk?
2. TOP RISKS — Which categories are projected to exceed budget? By how much ($)?
3. BRIGHT SPOTS — Which categories are well within budget?
4. ONE ACTION — The single most impactful change the user could make this month.

Use specific dollar amounts. Be direct but encouraging. Return only the paragraph, no JSON, no headers."""


def generate_budget_forecast(rolling_averages: dict, budget_limits: dict) -> str:
    context = "3-month rolling average spending vs. budget:\n"
    over, on_track, no_budget = [], [], []

    for cat, avg in sorted(rolling_averages.items(), key=lambda x: x[1], reverse=True):
        limit = budget_limits.get(cat)
        if limit:
            pct = (avg / limit) * 100
            status = "OVER BUDGET" if pct >= 100 else ("AT RISK" if pct >= 90 else "on track")
            context += f"  {cat}: ${avg:.2f}/mo avg vs ${limit:.2f} limit ({pct:.0f}%) — {status}\n"
            if pct >= 90:
                over.append(cat)
            else:
                on_track.append(cat)
        else:
            context += f"  {cat}: ${avg:.2f}/mo avg — no budget set\n"
            no_budget.append(cat)

    if over:
        context += f"\nAt-risk categories: {', '.join(over)}"
    if on_track:
        context += f"\nOn-track categories: {', '.join(on_track[:3])}"

    text, _ = complete(
        system=_FORECAST_SYSTEM,
        user=context,
        max_tokens=300,
        priority=FORECAST,
    )
    return text.strip()
