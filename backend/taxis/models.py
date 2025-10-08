from __future__ import annotations

import database
from fastapi import HTTPException, status
from sqlalchemy import Integer, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy_utils import generic_repr

from .schemas import TaxiStatus


@generic_repr
class Taxi(database.Base):
    __tablename__ = "taxis"

    pk: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    status: Mapped[str] = mapped_column(default=TaxiStatus.AVAILABLE, nullable=False)
    x: Mapped[int] = mapped_column(nullable=False)
    y: Mapped[int] = mapped_column(Integer, nullable=False)

    @staticmethod
    async def get_nearest_taxi(
        db_session: AsyncSession, x_start: int, y_start: int
    ) -> Taxi | None:
        query = (
            select(Taxi)
            .where(Taxi.status == TaxiStatus.AVAILABLE)
            .order_by(
                (func.pow(Taxi.x - x_start, 2) + func.pow(Taxi.y - y_start, 2)).asc()
            )
        ).limit(1)
        return (await db_session.scalars(query)).first()

    @staticmethod
    async def get_by_pk(db_session: AsyncSession, pk: int) -> Taxi | None:
        return (
            await db_session.scalars(select(Taxi).where(Taxi.pk == pk).limit(1))
        ).first()

    @staticmethod
    async def get_by_pk_or_404(db_session: AsyncSession, pk: int) -> Taxi:
        taxi = await Taxi.get_by_pk(db_session, pk)
        if taxi is None:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND, detail=f"Taxi(pk={pk}) not found"
            )
        return taxi

    @staticmethod
    async def update_taxi_available_and_location(
        db_session: AsyncSession, taxi_id: int, new_x: int, new_y: int
    ) -> Taxi:
        taxi = await Taxi.get_by_pk_or_404(db_session, taxi_id)
        taxi.status = TaxiStatus.AVAILABLE
        taxi.x = new_x
        taxi.y = new_y
        await db_session.commit()
        return taxi
