from typing import Annotated, Any

from database import get_db
from fastapi import APIRouter, Depends
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import apaginate
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Event
from .schemas import EventResponse, EventType

router = APIRouter(prefix="/events", tags=["events"])


@router.get("", response_model=Page[EventResponse])
async def get_events(
    db_session: Annotated[AsyncSession, Depends(get_db)],
) -> Any:
    return await apaginate(db_session, select(Event).order_by(Event.created_at.desc()))


@router.post("", response_model=EventResponse)
async def post_event(
    event_type: EventType,
    taxi_id: int | None = None,
    trip_id: int | None = None,
    user_id: int | None = None,
    db_session: AsyncSession = Depends(get_db),
) -> Event:
    return await Event(
        event_type=event_type, taxi_id=taxi_id, trip_id=trip_id, user_id=user_id
    ).create(db_session)
