from fastapi import APIRouter, UploadFile, File, HTTPException
from db.supabase import get_client
from services.csv_parser import parse_csv
from services.categorizer import categorize_transactions_bulk, _persist_learned
from services.error_logger import log_error
from models.transaction import TransactionUpdate
import math
import uuid

router = APIRouter(prefix="/transactions", tags=["transactions"])


def _clean(obj):
    """Recursively replace NaN/Inf floats with None so the payload is JSON-safe."""
    if isinstance(obj, dict):
        return {k: _clean(v) for k, v in obj.items()}
    if isinstance(obj, float) and (math.isnan(obj) or math.isinf(obj)):
        return None
    return obj


@router.post("/import/csv")
async def import_csv(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(400, "Only CSV files are supported")

    content = await file.read()
    try:
        transactions = parse_csv(content)
    except ValueError as e:
        log_error("csv_import", e, {"filename": file.filename})
        raise HTTPException(400, str(e))

    if not transactions:
        raise HTTPException(400, "No valid transactions found in CSV")

    descriptions = [t.description for t in transactions]
    categories_map = categorize_transactions_bulk(descriptions)

    db = get_client()
    cats = db.table("categories").select("id, name").execute().data
    cat_id_map = {c["name"]: c["id"] for c in cats}

    rows = []
    for t in transactions:
        cat_name = categories_map.get(t.description, "Other")
        rows.append({
            "date": t.date.isoformat(),
            "description": t.description,
            "amount": t.amount,
            "merchant": t.merchant,
            "category_id": cat_id_map.get(cat_name),
            "raw_csv_row": _clean(t.raw_csv_row),
            "external_ref": t.external_ref,
        })

    try:
        db.table("transactions").upsert(rows, on_conflict="external_ref", ignore_duplicates=True).execute()
    except Exception as e:
        log_error("csv_import_db", e, {"filename": file.filename, "row_count": len(rows)})
        raise HTTPException(500, "Failed to save transactions to database")

    return {"imported": len(rows), "message": f"Successfully imported {len(rows)} transactions"}


@router.get("/")
def list_transactions(month_year: str | None = None, limit: int = 100):
    db = get_client()
    query = (
        db.table("transactions")
        .select("*, categories(name, color, icon)")
        .order("date", desc=True)
        .limit(limit)
    )
    if month_year:
        # Filter by month: month_year = "2024-01"
        start = f"{month_year}-01"
        year, month = month_year.split("-")
        next_month = f"{int(year)}-{int(month)+1:02d}-01" if int(month) < 12 else f"{int(year)+1}-01-01"
        query = query.gte("date", start).lt("date", next_month)

    return query.execute().data


@router.patch("/{transaction_id}")
def update_category(transaction_id: uuid.UUID, body: TransactionUpdate):
    db = get_client()
    db.table("transactions").update(
        {"category_id": str(body.category_id)}
    ).eq("id", str(transaction_id)).execute()

    # Persist the user correction so future imports skip the AI call for this description
    tx = (
        db.table("transactions")
        .select("description, categories(name)")
        .eq("id", str(transaction_id))
        .execute()
        .data
    )
    if tx:
        desc = tx[0]["description"]
        cat_name = (tx[0].get("categories") or {}).get("name")
        if cat_name:
            _persist_learned({desc: cat_name}, source="user")

    return {"success": True}


@router.get("/summary/monthly")
def monthly_summary(month_year: str):
    db = get_client()
    start = f"{month_year}-01"
    year, month = month_year.split("-")
    next_month = f"{int(year)}-{int(month)+1:02d}-01" if int(month) < 12 else f"{int(year)+1}-01-01"

    rows = (
        db.table("transactions")
        .select("amount, categories(name)")
        .gte("date", start)
        .lt("date", next_month)
        .execute()
        .data
    )

    totals: dict[str, float] = {}
    for row in rows:
        cat = row.get("categories", {})
        name = cat.get("name", "Other") if cat else "Other"
        totals[name] = round(totals.get(name, 0) + row["amount"], 2)

    return totals
