import datetime as dt

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from dispatch_events.models import Event
from dispatch_events.schemas import EventType


# Move this to test_utils if more modules use it
def format_dt(date: dt.datetime) -> str:
    return date.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


@pytest.mark.asyncio
async def test_get_events(
    db_session: AsyncSession, client: AsyncClient, dt_mock: dt.datetime
) -> None:
    await Event(
        event_type=EventType.TAXI_ASSIGNMENT,
        taxi_id=1,
        trip_id=1,
        user_id=12,
        created_at=dt_mock,
    ).create(db_session)

    await Event(
        event_type=EventType.CLIENT_PICKUP,
        taxi_id=1,
        trip_id=1,
        user_id=12,
        created_at=dt_mock,
    ).create(db_session)

    response = await client.get("/events")
    assert response.status_code == 200, response.text
    assert response.json() == {
        "items": [
            {
                "taxi_id": 1,
                "trip_id": 1,
                "user_id": 12,
                "event_type": "taxi_assignment",
                "created_at": format_dt(dt_mock),
                "pk": 1,
            },
            {
                "taxi_id": 1,
                "trip_id": 1,
                "user_id": 12,
                "event_type": "client_pickup",
                "created_at": format_dt(dt_mock),
                "pk": 2,
            },
        ],
        "total": 2,
        "page": 1,
        "size": 50,
        "pages": 1,
    }


@pytest.mark.asyncio
async def test_create_event(client: AsyncClient, dt_mock: dt.datetime) -> None:
    response = await client.post(
        "/events?event_type=taxi_assignment&taxi_id=1&trip_id=1&user_id=12"
    )
    assert response.status_code == 200, response.text
    assert response.json() == {
        "taxi_id": 1,
        "trip_id": 1,
        "user_id": 12,
        "event_type": "taxi_assignment",
        "created_at": format_dt(dt_mock),
        "pk": 1,
    }


@pytest.mark.asyncio
async def test_create_event_no_optional_fields(
    client: AsyncClient, dt_mock: dt.datetime
) -> None:
    response = await client.post("/events?event_type=client_delivery")
    assert response.status_code == 200, response.text
    assert response.json() == {
        "taxi_id": None,
        "trip_id": None,
        "user_id": None,
        "event_type": "client_delivery",
        "created_at": format_dt(dt_mock),
        "pk": 1,
    }
