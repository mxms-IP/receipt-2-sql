# app/api/routes/expenses.py

import base64

from fastapi import APIRouter, File, HTTPException, UploadFile
from app.models.requests import ExtractRequest, ImageExtractRequest
from app.models.expense import Expense
from app.services.llm.gemini import GeminiClient
from app.services.audio.whisper import WhisperClient
import tempfile


router = APIRouter(prefix="/expenses", tags=["expenses"])

client = GeminiClient()
whisper = WhisperClient()

ALLOWED_MIME_TYPES = ["image/jpeg","image/jpg", "image/png", "image/webp", "audio/mp3", "audio/wav", "audio/ogg", "audio/m4a"]
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

@router.post("/extract_from_audio")
async def extract_expense_from_audio(file: UploadFile = File(...)):

    contents= await file.read() #gets bytes

    if file.content_type not in ALLOWED_MIME_TYPES:
            raise HTTPException(status_code=400, detail="Unsupported format. Supported formats are mp3, wav, ogg, m4a.")
        

    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
        tmp.write(contents)
        tmp_path = tmp.name 

    content_text= whisper.transcribe(tmp_path) #returns transcribed text

    response=   await client.extract_expense(content_text)

    return response

    

    #get the audio call whisper transcribe, before that check fro valid allowedtypes, then once transcribed send to extract_from_text function of geminiclient




