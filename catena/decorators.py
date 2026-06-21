from functools import wraps
from typing import Any
from typing import Callable

import broker

from catena import appdata
from catena import namespace


def update_status(status: str) -> Callable:
    """
    Decorator that updates the status bar for the duration of the decorated
    function with the given status.
    Status bar is reset to idle after func is finished executing.

    Args:
        status (str): The status to signal during func execution.
    """

    def decorator(func: Callable) -> Callable:

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            broker.emit(namespace.STATUS_CHANGED, status=status)
            val = func(*args, **kwargs)
            broker.emit(namespace.STATUS_CHANGED, status=appdata.STATUS_IDLE)
            return val

        return wrapper

    return decorator
