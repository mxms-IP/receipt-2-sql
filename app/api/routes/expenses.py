# app/api/routes/expenses.py

from fastapi import APIRouter
from app.models.requests import ExtractRequest
from app.models.expense import Expense
from app.services.llm.gemini import GeminiClient

router = APIRouter(prefix="/expenses", tags=["expenses"])

client = GeminiClient()


@router.post("/extract")
async def extract_expense(request: ExtractRequest) -> Expense:
    # take the raw_text from the request object
    # and pass it to client.extract_expense()
 
    raw_input= request.raw_text
    response=   await  client.extract_expense(raw_input)

    return response




