from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from datetime import date, timedelta
from typing import Optional
from services.gemini_chat import stream_chat_response
from db.supabase import get_client

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatMessage(BaseModel):
    role: str  # "user" or "model"
    text: str


class ChatRequest(BaseModel):
    message: str
    history: list[ChatMessage] = []
    include_spending_context: bool = True


def _get_recent_spending() -> dict | None:
    db = get_client()
    cutoff = (date.today().replace(day=1) - timedelta(days=1)).replace(day=1)
    rows = (
        db.table("transactions")
        .select("amount, categories(name)")
        .gte("date", cutoff.isoformat())
        .lt("amount", 0)
        .execute()
        .data
    )
    if not rows:
        return None

    totals: dict[str, float] = {}
    for row in rows:
        cat = row.get("categories", {})
        name = cat.get("name", "Other") if cat else "Other"
        totals[name] = round(totals.get(name, 0) + abs(row["amount"]), 2)
    return totals


@router.post("/")
async def chat(req: ChatRequest):
    spending = _get_recent_spending() if req.include_spending_context else None

    # Convert history to Gemini format
    history = [
        {"role": msg.role, "parts": [{"text": msg.text}]}
        for msg in req.history[-6:]  # keep last 6 messages for context
    ]

    def generate():
        for chunk in stream_chat_response(req.message, history, spending):
            yield chunk

    return StreamingResponse(generate(), media_type="text/plain")
