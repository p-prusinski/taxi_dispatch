import datetime as dt
import random

import pytest
from dispatch_events.models import Event
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from taxis.models import Taxi
from taxis.schemas import TaxiStatus
from tests.test_utils import serialize_model

PATH = "trips.router"


@patch(f"{PATH}.send_request_to_taxi")
@pytest.mark.asyncio
async def test_order_trip(
    taxi_request_mock: AsyncMock,
    db_session: AsyncSession,
    client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    await Taxi(x=10, y=15, callback_url="http://mockurl:8080").create(db_session)

    monkeypatch.setattr(random, "choices", lambda _, **kwargs: [2] * kwargs["k"])

    body = {
        "user_id": 1,
        "x_start": 0,
        "y_start": 2,
        "x_destination": 13,
        "y_destination": 16,
    }
    response = await client.post("/trips", json=body)
    taxi_request_mock.assert_called_once()
    assert response.status_code == 200, response.text
    assert response.json() == {
        "taxi_id": 1,
        "user_id": 1,
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
    await Taxi(
        x=10, y=15, status=TaxiStatus.BUSY, callback_url="http://mockurl:8080"
    ).create(db_session)

    body = {
        "user_id": 1,
        "x_start": 0,
        "y_start": 2,
        "x_destination": 13,
        "y_destination": 16,
    }
    response = await client.post("/trips", json=body)
    assert response.status_code == 404, response.text
    assert response.json() == {
        "detail": "No taxis available right now, please try again later"
    }


@patch(f"{PATH}.send_request_to_taxi")
@pytest.mark.asyncio
async def test_order_trip_creates_event(
    taxi_request_mock: AsyncMock,
    db_session: AsyncSession,
    client: AsyncClient,
    dt_mock: dt.datetime,
) -> None:
    await Taxi(pk=3, x=10, y=15, callback_url="http://mockurl:8080").create(db_session)

    body = {
        "user_id": 2,
        "x_start": 0,
        "y_start": 2,
        "x_destination": 13,
        "y_destination": 16,
    }
    response = await client.post("/trips", json=body)
    taxi_request_mock.assert_called_once()
    assert response.status_code == 200, response.text

    event = (await Event.get_all(db_session))[0]
    assert serialize_model(event) == {
        "taxi_id": 3,
        "trip_id": 1,
        "user_id": 2,
        "event_type": "taxi_assignment",
        "created_at": dt_mock,
        "pk": 1,
    }
