from typing import Annotated
from pydantic import BaseModel, Field
from enum import Enum

Coordinate = Annotated[
    int,
    Field(
        gte=0,
        le=100,
        examples=[90],
    ),
]


class TaxiStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    BUSY = "BUSY"


class TaxiBase(BaseModel):
    x: Coordinate
    y: Coordinate
    status: TaxiStatus


class TaxiCreate(TaxiBase):
    pass


class TaxiResponse(TaxiBase):
    pass


class TaxiListResponse(TaxiBase):
    id: int
