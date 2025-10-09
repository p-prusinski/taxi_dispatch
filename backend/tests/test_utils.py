import datetime as dt


def format_dt(date: dt.datetime) -> str:
    return date.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
