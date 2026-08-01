from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from config import DATABASE_URL

engine = create_async_engine(DATABASE_URL)

AsyncSessionLocal = async_sessionmaker(bind=engine)

class Base(DeclarativeBase):
    pass

async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
