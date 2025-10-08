import datetime as dt
from enum import Enum

from pydantic import BaseModel


class EventType(str, Enum):
    TAXI_REGISTER = "taxi_register"
    TAXI_ASSIGNMENT = "taxi_assignment"
    CLIENT_PICKUP = "client_pickup"
    CLIENT_DELIVERY = "client_delivery"


class EventBase(BaseModel):
    taxi_id: int | None
    trip_id: int | None
    user_id: int | None


class EventResponse(EventBase):
    event_type: EventType
    created_at: dt.datetime
    pk: int
