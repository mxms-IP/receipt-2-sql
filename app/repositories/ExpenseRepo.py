from app.core.database import AsyncSessionLocal, ExpenseDB
from app.models.expense import Expense
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.reponse import ExpenseResponse

class ExpenseRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def save(self, expense: Expense) -> ExpenseResponse:
        db_expense = ExpenseDB(
            amount=expense.amount,
            currency=expense.currency,
            category=expense.category,
            vendor = expense.vendor,
            date = expense.date,
            description = expense.description,
            confidence= expense.confidence,
            raw_input= expense.raw_input,
            needs_review= expense.needs_review
          
    
        )
        self.db.add(db_expense)

        await self.db.commit()
        await self.db.refresh(db_expense)
        
        expense_response = ExpenseResponse.model_validate(db_expense)

        return expense_response