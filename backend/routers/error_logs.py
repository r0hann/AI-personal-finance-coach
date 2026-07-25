from fastapi import APIRouter
from db.supabase import get_client

router = APIRouter(prefix="/error-logs", tags=["error-logs"])


@router.get("/")
def list_error_logs(limit: int = 50):
    return (
        get_client()
        .table("error_logs")
        .select("id, timestamp, source, error_type, message, details")
        .order("timestamp", desc=True)
        .limit(limit)
        .execute()
        .data
    )


@router.delete("/")
def clear_error_logs():
    get_client().table("error_logs").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
    return {"success": True}
