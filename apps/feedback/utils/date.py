from datetime import date, time
from functools import singledispatch
from typing import Any


@singledispatch
def to_message_format(data: Any) -> str:
    """Format date or datetime to message format."""
    raise NotImplementedError(f"There is no approach for type {type(data)}")


@to_message_format.register(date)
def _(data: date) -> str:
    return data.strftime('%d.%m.%Y')


@to_message_format.register(time)
def _(data: time) -> str:
    return data.strftime("%H:%M")
