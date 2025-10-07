from __future__ import annotations

import database
from sqlalchemy import Integer
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy_utils import generic_repr

from .schemas import TaxiStatus


@generic_repr
class Taxi(database.Base):
    __tablename__ = "taxis"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    status: Mapped[str] = mapped_column(default=TaxiStatus.AVAILABLE, nullable=False)
    x: Mapped[int] = mapped_column(nullable=False)
    y: Mapped[int] = mapped_column(Integer, nullable=False)
