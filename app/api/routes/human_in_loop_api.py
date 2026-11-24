

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db
from app.repositories.ExpenseRepo import ExpenseRepository

review_router= APIRouter(prefix="/review", tags=["review"])

@review_router.get("/expenses/review-queue")
async def needs_reviews(db: AsyncSession = Depends(get_db)):

    db_expense= ExpenseRepository(db)
    response= await db_expense.get_needs_review()

    return response

@review_router.put("/expenses/{id}/approve")
async def approve(id: str, db: AsyncSession = Depends(get_db)):

    db_expense= ExpenseRepository(db)
    response = await db_expense.get_expenseby_id(id)

    approved_response= await db_expense.approve(response)

    return {"status": "approved", "response": approved_response}