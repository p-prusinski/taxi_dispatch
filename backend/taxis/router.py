from typing import Annotated, Any

from database import get_db
from fastapi import APIRouter, Depends
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import apaginate
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Taxi
from .schemas import TaxiCreate, TaxiListResponse, TaxiResponse

router = APIRouter(prefix="/taxis", tags=["taxis"])


@router.post("/register", response_model=TaxiResponse)
async def register_taxi(
    req: TaxiCreate, db_session: AsyncSession = Depends(get_db)
) -> Taxi:
    return await Taxi(x=req.x, y=req.y).create(db_session)


@router.get("", response_model=Page[TaxiListResponse])
async def get_taxis(
    db_session: Annotated[AsyncSession, Depends(get_db)],
) -> Any:
    return await apaginate(db_session, select(Taxi).order_by(Taxi.status.asc()))
