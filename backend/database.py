import logging
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base

from config import settings

logger = logging.getLogger(__name__)

Base = declarative_base()

engine = create_async_engine(settings.db_config, echo=True)

AsyncSessionFactory = async_sessionmaker(bind=engine, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionFactory() as session:
        logger.debug(f"ASYNC POOL: {engine.pool.status()}")
        yield session
