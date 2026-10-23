from enum import Enum
from typing import Optional
from pydantic import BaseModel
from datetime import date, datetime

class Expense(BaseModel):
    amount: float
    currency: Currency
    category: ExpenseCategory
    vendor: Optional[str]
    date: date
    description: Optional[str]
    confidence: float
    raw_input: str
    needs_review: bool
    


class ExpenseCategory(str, Enum):
    FOOD_DINING = "Food & Dining"
    TRANSPORT = "Transport"
    UTILITIES = "Utilities"           # Electricity, gas, water
    HEALTHCARE = "Healthcare"
    EDUCATION = "Education"
    GROCERY = "Grocery"
    CLOTHING = "Clothing"
    ENTERTAINMENT = "Entertainment"
    RENT = "Rent"
    MOBILE_INTERNET = "Mobile & Internet"
    FUEL = "Fuel"
    HOUSEHOLD = "Household"
    PERSONAL_CARE = "Personal Care"
    OTHER = "Other"

class Currency(str, Enum):
    PKR = "PKR"    # Pakistani Rupee — the default
    USD = "USD"    # For international transactions
    AED = "AED"    # UAE Dirham — common for remittances in Pakistan
    GBP = "GBP"
    SAR = "SAR"    # Saudi Riyal — another common remittance currency