from pydantic import BaseModel
from taxis.schemas import Coordinate


class TripBase(BaseModel):
    x_start: Coordinate
    y_start: Coordinate
    x_destination: Coordinate
    y_destination: Coordinate


class TripCreate(TripBase):
    pass


class TripResponse(TripBase):
    taxi_id: int
    waiting_time_minutes: int
    travel_time_minutes: int
