from app.core.database import AsyncSessionLocal
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator


# routes dependency, create new session for every request
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
