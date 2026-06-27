from catena.preferences import preferences

__all__ = ["get_texture_resolution"]

_prefs = preferences.Preferences()


def get_texture_resolution() -> tuple[int, int]:
    """Returns the texture resolution as a tuple[int, int]."""
    x = _prefs.general_preferences.texture_resolution
    return (x, x)
