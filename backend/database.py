import logging
from collections.abc import AsyncGenerator, Sequence
from typing import Self

from config import settings
from sqlalchemy import select
from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

logger = logging.getLogger(__name__)


class Base(AsyncAttrs, DeclarativeBase):
    async def create(self, db: AsyncSession, refresh: bool = True) -> Self:
        db.add(self)
        await db.commit()
        if refresh:
            await db.refresh(self)
        return self

    @classmethod
    async def get_all(cls, db_session: AsyncSession) -> Sequence[Self]:
        return (await db_session.scalars(select(cls))).all()

    async def delete(self, db_session: AsyncSession) -> None:
        await db_session.delete(self)
        await db_session.commit()


engine = create_async_engine(settings.db_config, echo=True)
AsyncSessionFactory = async_sessionmaker(bind=engine, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionFactory() as session:
        logger.debug(f"ASYNC POOL: {engine.pool.status()}")
        yield session
