from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field, HttpUrl, field_validator

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
    callback_url: str = "http://example:8080"

    @field_validator("callback_url")
    @classmethod
    def validate_callback_url(cls, value: str) -> str:
        url = HttpUrl(value)
        return str(url)


class TaxiUpdate(TaxiBase):
    pass


class TaxiResponse(TaxiBase):
    status: TaxiStatus
    callback_url: HttpUrl
    pk: int


class TaxiListResponse(TaxiBase):
    status: TaxiStatus
    callback_url: str
    pk: int
