import uuid
from sqlalchemy import Column, DateTime, String, Boolean, Float, Numeric, Date
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime, timezone
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.core.config import get_settings



settings = get_settings()

engine= create_async_engine(settings.DATABASE_URL)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

default = lambda: datetime.now(timezone.utc)

class Base(DeclarativeBase):
    pass

class ExpenseDB(Base):
    __tablename__ = "expenses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    amount = Column(Numeric)
    currency= Column(String, default="PKR") 
    category = Column(String)
    vendor = Column(String, nullable=True)
    date = Column(Date)
    description = Column(String, nullable=True)
    confidence= Column(Float)
    raw_input= Column(String) 
    needs_review= Column(Boolean)
   

