from datetime import datetime


def get_current_utc_time():
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")


def string_to_datetime(timestamp: str) -> datetime:
    return datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
