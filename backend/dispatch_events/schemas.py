from enum import Enum


class EventType(str, Enum):
    TAXI_REGISTER = "taxi_register"
    TAXI_ASSIGNMENT = "taxi_assignment"
    CLIENT_PICKUP = "client_pickup"
    CLIENT_DELIVERY = "client_delivery"
