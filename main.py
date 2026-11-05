# app/main.py

from contextlib import asynccontextmanager

from fastapi import FastAPI
from app.api.routes.expense_api import router
from app.core.database import Base, engine



@asynccontextmanager
async def lifespan(app: FastAPI):
    # Correct way to create tables with an AsyncEngine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(
    title="AI Expense Tracker",
    version="0.1.0",
    lifespan=lifespan
)

app.include_router(router)

@app.get("/home")
def home():
    return {"message": "AI Expense Tracker is running"}

@app.get("/health")
def health():
    return {"status": "ok"}