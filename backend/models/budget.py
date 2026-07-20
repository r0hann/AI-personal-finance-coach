from pydantic import BaseModel
from typing import Optional
import uuid


class Budget(BaseModel):
    id: Optional[uuid.UUID] = None
    category_id: uuid.UUID
    monthly_limit: float
    month_year: str  # "2024-01"


class BudgetCreate(BaseModel):
    category_id: uuid.UUID
    monthly_limit: float
    month_year: str
