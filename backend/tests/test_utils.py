import datetime as dt
from typing import Any


def format_dt(date: dt.datetime) -> str:
    return date.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def serialize_model(model: Any) -> dict[str, object]:
    result = {}
    for col in model.__table__.columns.keys():
        val = getattr(model, col)
        result[col] = val
    return result
