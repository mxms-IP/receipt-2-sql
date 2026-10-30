# app/main.py

from fastapi import FastAPI
from app.api.routes.expense_api import router


app = FastAPI(
    title="AI Expense Tracker",
    version="0.1.0"
)

app.include_router(router)

@app.get("/home")
def home():
    return {"message": "AI Expense Tracker is running"}

@app.get("/health")
def health():
    return {"status": "ok"}