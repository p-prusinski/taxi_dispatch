import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from taxis.models import Taxi
from taxis.schemas import TaxiStatus


@pytest.mark.asyncio
async def test_get_nearest_taxi(db_session: AsyncSession) -> None:
    taxi1 = await Taxi(x=1, y=12).create(db_session)
    await Taxi(x=100, y=100).create(db_session)

    nearest_taxi = await Taxi.get_nearest_taxi(db_session, 5, 5)
    assert nearest_taxi == taxi1


@pytest.mark.asyncio
async def test_get_nearest_taxi_busy_taxis_return_none(
    db_session: AsyncSession,
) -> None:
    await Taxi(x=1, y=12, status=TaxiStatus.BUSY).create(db_session)
    await Taxi(x=100, y=100, status=TaxiStatus.BUSY).create(db_session)
    assert await Taxi.get_nearest_taxi(db_session, 5, 5) is None
