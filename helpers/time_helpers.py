from datetime import datetime


def get_current_utc_time():
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")


def string_to_datetime(timestamp: str | None) -> datetime:
    if timestamp is None:
        return datetime.min
    return datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
