from pathlib import Path
from typing import Union

JSON_TYPE = Union[dict, list, int, float, bool, str, None]

_APPDATA_PATH = Path.home() / "Appdata"
_APPDATA_ROAMING_PATH = _APPDATA_PATH / "Roaming"

CATENA_APPDATA_PATH = _APPDATA_ROAMING_PATH / "Catena"
CATENA_APPDATA_PATH.mkdir(parents=True, exist_ok=True)

CATENA_PREFERENCES_PATH = CATENA_APPDATA_PATH / "Preferences.json"
CATENA_SESSION_DATA_PATH = CATENA_APPDATA_PATH / "SessionData.json"

CATENA_FILE_SUFFIX = ".cg"
INITIAL_CATENA_FILE = CATENA_APPDATA_PATH / f"__catena_initial__{CATENA_FILE_SUFFIX}"
