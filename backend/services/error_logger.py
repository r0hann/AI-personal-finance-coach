import logging
import traceback
from typing import Any
from db.supabase import get_client

log = logging.getLogger(__name__)


def log_error(source: str, error: Exception, details: dict[str, Any] | None = None) -> None:
    """Write an error record to the error_logs table. Never raises — logging must not crash the app."""
    try:
        payload = {
            "source": source,
            "error_type": type(error).__name__,
            "message": str(error),
            "details": {
                "traceback": traceback.format_exc(),
                **(details or {}),
            },
        }
        get_client().table("error_logs").insert(payload).execute()
    except Exception as e:
        log.warning("Failed to write to error_logs: %s", e)
