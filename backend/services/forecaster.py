"""Budget forecasting: 3-month rolling averages and over-budget detection."""
from collections import defaultdict
from datetime import date, timedelta
from db.supabase import get_client


def get_rolling_averages(months: int = 3) -> dict[str, float]:
    """Calculate average monthly spending per category over the past N months."""
    db = get_client()
    cutoff = (date.today().replace(day=1) - timedelta(days=1)).replace(day=1)
    for _ in range(months - 1):
        cutoff = (cutoff - timedelta(days=1)).replace(day=1)

    rows = (
        db.table("transactions")
        .select("amount, category_id, categories(name)")
        .gte("date", cutoff.isoformat())
        .lt("amount", 0)  # expenses are negative in standard bank CSVs
        .execute()
        .data
    )

    monthly_totals: dict[str, list[float]] = defaultdict(list)
    for row in rows:
        cat = row.get("categories", {})
        if cat and cat.get("name"):
            monthly_totals[cat["name"]].append(abs(row["amount"]))

    return {cat: sum(amounts) / months for cat, amounts in monthly_totals.items()}


def get_budget_limits(month_year: str) -> dict[str, float]:
    """Fetch budget limits for a given month."""
    db = get_client()
    rows = (
        db.table("budgets")
        .select("monthly_limit, categories(name)")
        .eq("month_year", month_year)
        .execute()
        .data
    )
    return {
        row["categories"]["name"]: row["monthly_limit"]
        for row in rows
        if row.get("categories", {}).get("name")
    }


def get_over_budget_categories(rolling_averages: dict, budget_limits: dict) -> list[dict]:
    """Return categories projected to exceed 90% of their budget."""
    alerts = []
    for cat, avg in rolling_averages.items():
        limit = budget_limits.get(cat)
        if limit and avg >= limit * 0.9:
            alerts.append({
                "category": cat,
                "average_spend": round(avg, 2),
                "budget": round(limit, 2),
                "pct_used": round((avg / limit) * 100, 1),
            })
    return sorted(alerts, key=lambda x: x["pct_used"], reverse=True)
