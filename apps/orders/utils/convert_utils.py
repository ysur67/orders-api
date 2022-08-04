from datetime import date, datetime
from typing import Optional


def str_to_int(value: str) -> Optional[int]:
    try:
        return int(value)
    except ValueError:
        return None


def str_to_float(value: str) -> Optional[float]:
    try:
        return float(value)
    except ValueError:
        return None


def str_to_date(value: str) -> Optional[date]:
    try:
        return datetime.strptime(value, '%d.%m.%Y').date()
    except ValueError:
        return None
