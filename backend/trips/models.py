from __future__ import annotations

import random

import database
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy_utils import generic_repr
from taxis.models import Taxi


@generic_repr
class Trip(database.Base):
    __tablename__ = "trips"

    pk: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    taxi_id: Mapped[int] = mapped_column(ForeignKey("taxis.pk"), nullable=True)
    x_start: Mapped[int] = mapped_column(nullable=False)
    y_start: Mapped[int] = mapped_column(nullable=False)
    x_destination: Mapped[int] = mapped_column(nullable=False)
    y_destination: Mapped[int] = mapped_column(nullable=False)
    waiting_time_minutes: Mapped[int] = mapped_column(nullable=False)
    travel_time_minutes: Mapped[int] = mapped_column(nullable=False)

    @staticmethod
    def calculate_manhattan_distance(x1: int, y1: int, x2: int, y2: int) -> int:
        return abs(x2 - x1) + abs(y2 - y1)

    @classmethod
    def create_trip(
        cls,
        x_start: int,
        y_start: int,
        x_destination: int,
        y_destination: int,
        taxi: Taxi,
    ) -> Trip:
        travel_distance = cls.calculate_manhattan_distance(
            x_start, y_start, x_destination, y_destination
        )
        travel_time = sum(random.choices(range(1, 3), k=travel_distance))

        waiting_distance = cls.calculate_manhattan_distance(
            x_start, y_start, taxi.x, taxi.y
        )
        waiting_time = sum(random.choices(range(1, 3), k=waiting_distance))

        return cls(
            taxi_id=taxi.pk,
            x_start=x_start,
            y_start=y_start,
            x_destination=x_destination,
            y_destination=y_destination,
            waiting_time_minutes=waiting_time,
            travel_time_minutes=travel_time,
        )
