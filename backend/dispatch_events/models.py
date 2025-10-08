from __future__ import annotations

import datetime as dt
from typing import Any

import database
from fastapi import HTTPException, status
from sqlalchemy import DateTime, Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy_utils import generic_repr

from .schemas import EventType


@generic_repr
class Event(database.Base):
    __tablename__ = "events"

    pk: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    event_type: Mapped[str] = mapped_column(nullable=False)
    taxi_id: Mapped[int | None] = mapped_column(nullable=True)
    trip_id: Mapped[int | None] = mapped_column(nullable=True)
    user_id: Mapped[int | None] = mapped_column(nullable=True)
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: dt.datetime.now(dt.UTC)
    )

    @classmethod
    def sort_by_created(cls, query: Select[Any], order: str) -> Select[Any]:
        if order == "created_at":
            return query.order_by(cls.created_at.asc())
        return query.order_by(cls.created_at.desc())

    @staticmethod
    async def get_by_pk_or_404(db_session: AsyncSession, pk: int) -> Event:
        event_scalar = await db_session.scalars(
            select(Event).where(Event.pk == pk).limit(1)
        )
        event = event_scalar.first()
        if event is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Event({pk=}) not found"
            )
        return event
