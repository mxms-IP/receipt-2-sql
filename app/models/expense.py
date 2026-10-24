from decimal import Decimal
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, field_validator
from datetime import date


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
    USD = "USD"    
    AED = "AED"   
    GBP = "GBP"
    SAR = "SAR"   

class Expense(BaseModel):
    amount:       Decimal          = Field(gt=0, lt=Decimal("10000000"))    # cap 1 crore
    currency:     Currency         = Field(default=Currency.PKR)
    category:     ExpenseCategory
    vendor:       Optional[str]    = None
    date:         date
    description:  Optional[str]    = None
    confidence:   float            = Field(ge=0.0, le=1.0)
    raw_input:    str
    needs_review: bool             = Field(default=False)

    @field_validator("date")
    @classmethod
    def date_cannot_be_future(cls, v: date) -> date:
        """
        You can't have spent money tomorrow.
        This catches model hallucinations where it invents future dates.
        """
        if v > date.today():
            raise ValueError(
                f"Expense date {v} is in the future. "
                f"Today is {date.today()}."
            )
        return v
