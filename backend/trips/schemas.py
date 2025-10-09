from typing import Any

from pydantic import BaseModel, model_validator
from taxis.schemas import Coordinate


class TripBase(BaseModel):
    x_start: Coordinate
    y_start: Coordinate
    x_destination: Coordinate
    y_destination: Coordinate


class TripCreate(TripBase):
    user_id: int

    @model_validator(mode="before")
    @classmethod
    def validate_coordinates(cls, values: dict[str, Any]) -> dict[str, Any]:
        if (values.get("x_start") == values.get("x_destination")) and (
            values.get("y_start") == values.get("y_destination")
        ):
            raise ValueError(
                "Start coordinates must not be the same as destination coordinates"
            )

        return values


class TripResponse(TripBase):
    taxi_id: int
    user_id: int
    waiting_time_minutes: int
    travel_time_minutes: int
