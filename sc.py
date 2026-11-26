from pydantic import ValidationError
from app.models.expense import Expense

bad = {
    "amount": -5, "currency": "PKR", "category": "Grocery",
    "vendor": "Imtiaz", "date": "2026-11-25", "description": "test",
    "confidence": 0.9, "raw_input": "test",
}

try:
    Expense.model_validate(bad)
except ValidationError as e:
    print(e.errors()[0]["msg"])