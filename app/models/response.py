
from decimal import Decimal
from typing import Optional
import uuid
from pydantic import BaseModel
from datetime import date, datetime
from app.models.expense import Currency, ExpenseCategory


class ExpenseResponse(BaseModel):
    id: uuid.UUID
    amount: Decimal
    currency: Currency
    category: ExpenseCategory
    vendor: Optional[str]
    date: date
    needs_review: bool
    created_at: datetime
    

    class Config:
        from_attributes = True