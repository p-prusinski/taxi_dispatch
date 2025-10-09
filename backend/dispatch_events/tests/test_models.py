import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from dispatch_events.models import Event, add_event
from dispatch_events.schemas import EventType


@pytest.mark.asyncio
async def test_add_event(db_session: AsyncSession) -> None:
    event = await add_event(
        db_session=db_session,
        event_type=EventType.CLIENT_DELIVERY,
        taxi_id=None,
        trip_id=None,
        user_id=None,
    )
    assert (await Event.get_all(db_session))[0] == event
