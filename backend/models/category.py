from pydantic import BaseModel
from typing import Optional
import uuid


class Category(BaseModel):
    id: Optional[uuid.UUID] = None
    name: str
    color: str = "#6B7280"
    icon: str = "💰"
    is_custom: bool = False
