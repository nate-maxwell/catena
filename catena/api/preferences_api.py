from typing import Any
from typing import TypeVar

from catena.preferences.preferences import Preferences

__all__ = [
    "get_preferences",
    "list_preferences",
    "register_preferences",
    "save_preferences",
]

T = TypeVar("T")


def register_preferences(key: str, settings_cls: type[T]) -> T:
    """
    Register a dataclass-backed settings object with the shared preferences'
    singleton.

    The returned object is the live instance stored by Catena. Access it later
    with `get_preferences(key)` or `Preferences()[key]`, mutate it, then call
    `save_preferences()` to persist the updated values.
    """
    return Preferences().register_section(key, settings_cls)


def get_preferences(key: str) -> Any:
    """Return a previously registered settings object."""
    return Preferences().get_section(key)


def list_preferences() -> tuple[str, ...]:
    """Return the currently registered preference keys."""
    return Preferences().registered_keys()


def save_preferences() -> None:
    """
    Persist the current preferences snapshot to disk.

    Saving preferences emits a "prefs.updated" event. Subscribe to this event
    to allow systems to react to updates.
    """
    Preferences().save()
