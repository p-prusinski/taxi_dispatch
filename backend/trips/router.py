from database import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from taxis.models import Taxi
from taxis.schemas import TaxiStatus
from .models import Trip
from .schemas import TripCreate, TripResponse

router = APIRouter(prefix="/trips", tags=["trips"])


@router.post("/order", response_model=TripResponse)
async def order_trip(
    req: TripCreate, db_session: AsyncSession = Depends(get_db)
) -> Trip:
    db_session.begin()
    nearest_taxi = await Taxi.get_nearest_taxi(db_session, req.x_start, req.y_start)
    if nearest_taxi:
        nearest_taxi.status = TaxiStatus.BUSY
        trip = Trip().create_trip(
            taxi=nearest_taxi,
            x_start=int(req.x_start),
            y_start=int(req.y_start),
            x_destination=int(req.x_destination),
            y_destination=int(req.y_destination),
        )
        await trip.create(db_session)
        await db_session.commit()
        return trip
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="No taxis available right now, please try again later",
    )
