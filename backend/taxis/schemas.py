from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field

Coordinate = Annotated[
    int,
    Field(
        ge=0,
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


class TaxiCreate(TaxiBase):
    pass


class TaxiResponse(TaxiBase):
    status: TaxiStatus
    pk: int


class TaxiListResponse(TaxiBase):
    status: TaxiStatus
    pk: int
