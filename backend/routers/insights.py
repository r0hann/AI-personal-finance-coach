from fastapi import APIRouter
from datetime import date, timedelta
from db.supabase import get_client
from services.ai_coach import generate_monthly_insights

router = APIRouter(prefix="/insights", tags=["insights"])


def _get_spending_by_category(month_year: str) -> dict:
    db = get_client()
    start = f"{month_year}-01"
    year, month = month_year.split("-")
    next_month = f"{int(year)}-{int(month)+1:02d}-01" if int(month) < 12 else f"{int(year)+1}-01-01"

    rows = (
        db.table("transactions")
        .select("amount, categories(name)")
        .gte("date", start)
        .lt("date", next_month)
        .lt("amount", 0)  # expenses only
        .execute()
        .data
    )

    totals: dict[str, float] = {}
    for row in rows:
        cat = row.get("categories", {})
        name = cat.get("name", "Other") if cat else "Other"
        totals[name] = round(totals.get(name, 0) + abs(row["amount"]), 2)
    return totals


@router.get("/monthly")
def monthly_insights(month_year: str):
    db = get_client()

    # Check cache first (avoid re-calling AI on every page load)
    cached = (
        db.table("insights_cache")
        .select("content_json, generated_at")
        .eq("month_year", month_year)
        .execute()
        .data
    )
    if cached:
        from datetime import datetime
        generated = datetime.fromisoformat(cached[0]["generated_at"].replace("Z", "+00:00"))
        age_hours = (datetime.now(generated.tzinfo) - generated).total_seconds() / 3600
        if age_hours < 24:
            return cached[0]["content_json"]

    # Generate fresh insights
    spending = _get_spending_by_category(month_year)
    if not spending:
        return {"summary": "No spending data found for this month.", "insights": [], "savings_suggestions": []}

    # Get previous month for comparison
    year, month = month_year.split("-")
    prev_date = date(int(year), int(month), 1) - timedelta(days=1)
    prev_month_year = prev_date.strftime("%Y-%m")
    prev_spending = _get_spending_by_category(prev_month_year)

    insights = generate_monthly_insights(month_year, spending, prev_spending or None)

    # Cache the result
    db.table("insights_cache").upsert({
        "month_year": month_year,
        "content_json": insights,
    }).execute()

    return insights
