from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ExpenseCreate(BaseModel):
    amount: float
    category: str
    description: str = ""


class ExpenseUpdate(BaseModel):
    amount: Optional[float] = None
    category: Optional[str] = None
    description: Optional[str] = None


class ExpenseResponse(BaseModel):
    id: int
    amount: float
    category: str
    description: str
    date: datetime
    owner_id: int

    model_config = {"from_attributes": True}


class ExpenseStats(BaseModel):
    total_spent: float
    average_expense: float
    expense_count: int
    top_category: str
    by_category: dict[str, float]
