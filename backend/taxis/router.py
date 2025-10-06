from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from .schemas import TaxiResponse, TaxiCreate, TaxiListResponse
from .models import Taxi
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from typing import Annotated, Any

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
    return await paginate(db_session, select(Taxi).order_by(Taxi.status.asc()))
