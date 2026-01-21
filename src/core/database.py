from typing import AsyncGenerator

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from src.core.config import Configurations


Base = declarative_base()

class Database:
    """Database connection manager"""

    def __init__(self, config: Configurations):
        self.engine = create_async_engine(url=config.DATABASE_URL, echo=config.DB_ECHO, future=True)
        self.async_session = async_sessionmaker(self.engine, class_=AsyncSession, expire_on_commit=False)


async def get_db_session(request: Request) -> AsyncGenerator[AsyncSession, None]:

    db: Database = request.app.container.database()

    async with db.async_session() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
