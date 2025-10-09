from typing import Annotated, Any

from database import get_db
from dispatch_events.models import add_event
from dispatch_events.schemas import EventType
from fastapi import APIRouter, Depends
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import apaginate
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Taxi
from .schemas import TaxiCreate, TaxiListResponse, TaxiResponse

router = APIRouter(prefix="/taxis", tags=["taxis"])


@router.post("", response_model=TaxiResponse)
async def register_taxi(
    req: TaxiCreate, db_session: AsyncSession = Depends(get_db)
) -> Taxi:
    taxi = await Taxi(x=req.x, y=req.y).create(db_session)
    await add_event(db_session, event_type=EventType.TAXI_REGISTER, taxi_id=taxi.pk)
    return taxi


@router.get("", response_model=Page[TaxiListResponse])
async def get_taxis(
    db_session: Annotated[AsyncSession, Depends(get_db)],
) -> Any:
    return await apaginate(db_session, select(Taxi).order_by(Taxi.status.asc()))


@router.patch("/{pk}", response_model=TaxiResponse)
async def update_location_and_status_available(
    pk: int, req: TaxiCreate, db_session: Annotated[AsyncSession, Depends(get_db)]
) -> Taxi:
    return await Taxi.update_taxi_available_and_location(db_session, pk, req.x, req.y)
