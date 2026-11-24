

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db
from app.models.expense import Expense
from app.models.requests import ApproveRequest
from app.repositories.ExpenseRepo import ExpenseRepository

review_router= APIRouter(tags=["review"])

@review_router.get("/expenses/review-queue")
async def needs_reviews(db: AsyncSession = Depends(get_db)):

    db_expense= ExpenseRepository(db)
    response= await db_expense.get_needs_review()

    return response

@review_router.put("/expenses/{id}/approve")
async def approve(id: uuid.UUID , request: ApproveRequest, db: AsyncSession = Depends(get_db)):

    db_expense= ExpenseRepository(db)
    approved_response= await db_expense.update(id, request)

    if approved_response is None:
        raise HTTPException("404","This id does not exist")

    return {"status": "approved", "response": approved_response}