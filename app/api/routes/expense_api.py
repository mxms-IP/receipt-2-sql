# app/api/routes/expenses.py

import base64

from fastapi import APIRouter, File, HTTPException, UploadFile
from app.models.requests import ExtractRequest, ImageExtractRequest
from app.models.expense import Expense
from app.services.llm.gemini import GeminiClient

router = APIRouter(prefix="/expenses", tags=["expenses"])

client = GeminiClient()

ALLOWED_MIME_TYPES = ["image/jpeg","image/jpg", "image/png", "image/webp"]
MAX_FILE_SIZE = 5 * 1024 * 1024


@router.post("/extract_from_text")
async def extract_expense(request: ExtractRequest) -> Expense:
    # take the raw_text from the request object
    # and pass it to client.extract_expense()
 
    raw_input= request.raw_text
    response=   await client.extract_expense(raw_input)

    return response

#write a api endpoint that takes ExtractRequest but this time in image and feeds LLm
@router.post("/extract_from_image")
async def extract_expense_from_image(file: UploadFile = File(...)):

    content = await file.read()
    # Validation 1: check file.content_type is in ALLOWED_MIME_TYPES
    # if not, raise HTTPException with status_code=400
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported format. Supported formats are jpeg,jpg,png,webp.")
    
    # Validation 2: read the file bytes into a variable called content
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 5MB.")
    

    # Everything below is already done — don't change this part
    encoded_string = base64.b64encode(content).decode("utf-8")
    result = await client.extract_expense_from_image(encoded_string, file.content_type)
    return result




