from pydantic import BaseModel
from datetime import date
from typing import Optional
import uuid


class Transaction(BaseModel):
    id: Optional[uuid.UUID] = None
    date: date
    description: str
    amount: float
    merchant: Optional[str] = None
    category_id: Optional[uuid.UUID] = None
    raw_csv_row: Optional[dict] = None


class TransactionUpdate(BaseModel):
    category_id: uuid.UUID
