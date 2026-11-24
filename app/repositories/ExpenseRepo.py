import uuid

from sqlalchemy import select, text

from app.core.database import AsyncSessionLocal, ExpenseDB
from app.models.expense import Expense
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.requests import ApproveRequest
from app.models.response import ExpenseResponse

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

    async def get_needs_review(self) -> list:
        expenses= []
        stmt= text("SELECT * FROM expenses WHERE needs_review = True")
        response= await self.db.execute(stmt)
    
        
        for row in response.mappings().all():
            result= ExpenseResponse.model_validate(row)
            expenses.append(result)
        return expenses

    async def get_all(self)-> list:
        expenses= []
        stmt= text("SELECT * FROM expenses")
        response= await self.db.execute(stmt)

        for row in response.mappings().all():
            result= ExpenseResponse.model_validate(row)
            expenses.append(result)
        return expenses

    async def update(self,id: uuid.UUID, expense: ApproveRequest) -> ExpenseResponse:
        stmt= text ("""UPDATE expenses SET 
                                    amount= :amount, 
                                    currency= :currency, 
                                    category=:category, 
                                    vendor = :vendor, 
                                    date = :date, 
                                    description = :description, 
                                    needs_review= false 
                                WHERE id = :id 
                                RETURNING id, amount, currency, category, vendor, date, description,needs_review, created_at, updated_at""")

        dict= expense.model_dump()
        dict["id"]= id
        response = await self.db.execute(stmt,dict)

        await self.db.commit()

        row = response.mappings().first()
        expense_response = ExpenseResponse.model_validate(row) if row else None
        
        return expense_response

    async def get_expenseby_id(self, expense_id: uuid.UUID):

        stmt = text("""
                    SELECT *
                    FROM expenses 
                    WHERE id = :expense_id
                """)

        response= await self.db.execute(stmt,{"expense_id": expense_id})
        row = response.mappings().first()  # Extracts the row as a dict-like object (or None)

        if row is None:
            return None

        expense_response = ExpenseResponse.model_validate(row)

        return expense_response