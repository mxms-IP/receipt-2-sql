# app/api/routes/expenses.py

import base64

from fastapi import APIRouter, File, HTTPException, UploadFile
from app.dependencies import get_db
from app.models.reponse import ExpenseResponse
from app.models.requests import ExtractRequest, ImageExtractRequest
from app.models.expense import Expense
from app.repositories.ExpenseRepo import ExpenseRepository
from app.services.llm.gemini import GeminiClient
from app.services.llm.openrouter import OpenRouterClient
from app.services.audio.whisper import WhisperClient
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
import tempfile
import os


router = APIRouter(prefix="/expenses", tags=["expenses"])

#client = OpenRouterClient()
client= GeminiClient()
whisper = WhisperClient()

ALLOWED_MIME_TYPES = {
    "image/jpeg", "image/jpg", "image/png", "image/webp",
    "audio/mpeg", "audio/mp3", "audio/wav", "audio/x-wav", "audio/ogg", "audio/mp4", "audio/x-m4a"
}

MAX_FILE_SIZE = 5 * 1024 * 1024


@router.post("/extract_from_text")
async def extract_expense(request: ExtractRequest, db: AsyncSession = Depends(get_db)) -> ExpenseResponse:
    # take the raw_text from the request object
    # and pass it to client.extract_expense()
 
    raw_input= request.raw_text
    try:
        llm_response=   await client.extract_expense(raw_input)
    except ValueError as e:
        raise HTTPException(status_code=503, detail=str(e))

    db_expense= ExpenseRepository(db)
    db_response= await db_expense.save(llm_response)

    return db_response

@router.post("/extract_from_image")
async def extract_expense_from_image(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)) -> ExpenseResponse :

    content = await file.read()
    # Validation 1: check file.content_type is in ALLOWED_MIME_TYPES
    # if not, raise HTTPException with status_code=400
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported format. Supported formats are jpeg,jpg,png,webp.")
    
    # Validation 2: read the file bytes into a variable called content
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 5MB.")
    

    encoded_string = base64.b64encode(content).decode("utf-8")

    try:
        llm_response = await client.extract_expense_from_image(encoded_string, file.content_type)
    except ValueError as e:
            raise HTTPException(status_code=503, detail=str(e))

    db_expense= ExpenseRepository(db)
    db_response= await db_expense.save(llm_response)

    return db_response

@router.post("/extract_from_audio")
async def extract_expense_from_audio(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)) -> ExpenseResponse :

    
    if file.content_type not in ALLOWED_MIME_TYPES:
            raise HTTPException(status_code=400, detail="Unsupported format. Supported formats are mp3, wav, ogg, m4a.")
        

    contents= await file.read() #gets bytes
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
        tmp.write(contents)
        tmp_path = tmp.name 

    content_text= await whisper.transcribe(tmp_path) #returns transcribed text

    try:
        llm_response=  await client.extract_expense(content_text)
    except ValueError as e:
            raise HTTPException(status_code=503, detail=str(e))
    finally:
        os.remove(tmp_path)

    db_expense= ExpenseRepository(db)
    db_response= await db_expense.save(llm_response)

   
    return db_response

    

