from pathlib import Path
from typing import Union

JSON_TYPE = Union[dict, list, int, float, bool, str, None]

_APPDATA_PATH = Path.home() / "Appdata"
_APPDATA_ROAMING_PATH = _APPDATA_PATH / "Roaming"

CATENA_APPDATA_PATH = _APPDATA_ROAMING_PATH / "Catena"
CATENA_APPDATA_PATH.mkdir(parents=True, exist_ok=True)

CATENA_PREFERENCES_PATH = CATENA_APPDATA_PATH / "Preferences.json"

# temp
CATENA_GRAPH_FILE = CATENA_APPDATA_PATH / "last_graph.graph"
