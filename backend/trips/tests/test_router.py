import random

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from taxis.models import Taxi
from taxis.schemas import TaxiStatus


@pytest.mark.asyncio
async def test_order_trip(
    db_session: AsyncSession, client: AsyncClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    await Taxi(x=10, y=15).create(db_session)

    monkeypatch.setattr(random, "choices", lambda _, **kwargs: [2] * kwargs["k"])

    body = {"x_start": 0, "y_start": 2, "x_destination": 13, "y_destination": 16}
    response = await client.post("/trips", json=body)
    assert response.status_code == 200, response.text
    assert response.json() == {
        "taxi_id": 1,
        "travel_time_minutes": 54,
        "waiting_time_minutes": 46,
        "x_destination": 13,
        "x_start": 0,
        "y_destination": 16,
        "y_start": 2,
    }


@pytest.mark.asyncio
async def test_order_trip_no_taxis(
    db_session: AsyncSession, client: AsyncClient
) -> None:
    await Taxi(x=10, y=15, status=TaxiStatus.BUSY).create(db_session)

    body = {"x_start": 0, "y_start": 2, "x_destination": 13, "y_destination": 16}
    response = await client.post("/trips", json=body)
    assert response.status_code == 404, response.text
    assert response.json() == {
        "detail": "No taxis available right now, please try again later"
    }
