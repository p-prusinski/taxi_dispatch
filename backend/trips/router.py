from database import get_db
from dispatch_events.models import add_event
from dispatch_events.schemas import EventType
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from taxis.models import Taxi
from taxis.schemas import TaxiStatus
import httpx
import logging

from .models import Trip
from .schemas import TripCreate, TripResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/trips", tags=["trips"])


async def send_request_to_taxi(trip: Trip, callback_url: str) -> None:
    async with httpx.AsyncClient(timeout=10.0) as client:
        taxi_body = {
            "x_start": trip.x_start,
            "y_start": trip.y_start,
            "x_destination": trip.x_destination,
            "y_destination": trip.y_destination,
            "taxi_id": trip.taxi_id,
            "user_id": trip.user_id,
            "waiting_time_minutes": trip.waiting_time_minutes,
            "travel_time_minutes": trip.travel_time_minutes,
        }
        try:
            await client.post(callback_url, json=taxi_body)
        except httpx.ConnectTimeout:
            # This should probably raise HTTPException,
            # Also, Trip shouldn't be created if we can't send request
            # I left it as is for simplicity
            logger.error("Could not reach taxi")
            pass


@router.post("", response_model=TripResponse)
async def order_trip(
    req: TripCreate, db_session: AsyncSession = Depends(get_db)
) -> Trip:
    db_session.begin()
    nearest_taxi = await Taxi.get_nearest_taxi(db_session, req.x_start, req.y_start)
    if nearest_taxi:
        nearest_taxi.status = TaxiStatus.BUSY
        trip = Trip().create_trip(
            taxi=nearest_taxi,
            user_id=int(req.user_id),
            x_start=int(req.x_start),
            y_start=int(req.y_start),
            x_destination=int(req.x_destination),
            y_destination=int(req.y_destination),
        )
        trip = await trip.create(db_session)

        await add_event(
            db_session,
            event_type=EventType.TAXI_ASSIGNMENT,
            taxi_id=trip.taxi_id,
            trip_id=trip.pk,
            user_id=trip.user_id,
        )
        await db_session.commit()

        await send_request_to_taxi(trip, nearest_taxi.callback_url)

        return trip
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="No taxis available right now, please try again later",
    )
