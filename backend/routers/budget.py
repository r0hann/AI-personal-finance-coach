from fastapi import APIRouter
from pydantic import BaseModel
from datetime import date
from db.supabase import get_client
from services.forecaster import get_rolling_averages, get_budget_limits, get_over_budget_categories
from services.ai_coach import generate_budget_forecast
from models.budget import BudgetCreate

router = APIRouter(prefix="/budget", tags=["budget"])


@router.get("/forecast")
def forecast():
    month_year = date.today().strftime("%Y-%m")
    rolling = get_rolling_averages(months=3)
    limits = get_budget_limits(month_year)
    alerts = get_over_budget_categories(rolling, limits)
    narrative = generate_budget_forecast(rolling, limits) if rolling else ""

    return {
        "month_year": month_year,
        "rolling_averages": rolling,
        "budget_limits": limits,
        "over_budget_alerts": alerts,
        "narrative": narrative,
    }


@router.get("/")
def list_budgets(month_year: str | None = None):
    db = get_client()
    query = db.table("budgets").select("*, categories(name, color, icon)")
    if month_year:
        query = query.eq("month_year", month_year)
    return query.execute().data


@router.post("/")
def create_budget(body: BudgetCreate):
    db = get_client()
    db.table("budgets").upsert({
        "category_id": str(body.category_id),
        "monthly_limit": body.monthly_limit,
        "month_year": body.month_year,
    }).execute()
    return {"success": True}


@router.delete("/{budget_id}")
def delete_budget(budget_id: str):
    db = get_client()
    db.table("budgets").delete().eq("id", budget_id).execute()
    return {"success": True}
