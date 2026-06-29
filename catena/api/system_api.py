from catena.preferences import preferences
from catena.shortcuts import ShortcutManager

__all__ = ["get_texture_resolution", "ShortcutManager"]

_prefs = preferences.Preferences()


def get_texture_resolution() -> tuple[int, int]:
    """Returns the texture resolution as a tuple[int, int]."""
    x = _prefs.general_preferences.texture_resolution
    return (x, x)


ShortcutManager = ShortcutManager
"""Singleton system responsible for managing shortcuts across the application."""
