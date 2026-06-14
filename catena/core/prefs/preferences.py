from typing import Any
from typing import Optional
from dataclasses import asdict

import broker

from catena.core import appdata
from catena.core import io_utils
from catena.core import namespace
from catena.core.prefs.category_data import GeneralPreferences
from catena.core.prefs.category_data import NodeGraphPreferences
from catena.core.prefs.category_data import LayoutPreferences

GENERAL_PREFERENCES = "general_preferences"
GRAPH_PREFERENCES = "node_graph_preferences"
LAYOUT_PREFERENCES = "layout_preferences"


class AppdataError(Exception):
    """Errors for unhandled appdata values."""


class Preferences(object):
    """
    Singleton container holding all prefs data for the application.

    Checks roaming appdata for prefs file. If the file is found, class
    populates itself from file contents. Otherwise, file is created using class
    defaults.
    """

    _instance: Optional["Preferences"] = None

    def __new__(cls, *args: Any, **kwargs: Any) -> "Preferences":
        if cls._instance is None:
            cls._instance = super(Preferences, cls).__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        # Prevent re-initialization on subsequent calls
        if getattr(self, "_initialized", False):
            return
        self._initialized = True

        # Defaults
        self.general_preferences = GeneralPreferences()
        self.node_graph_preferences = NodeGraphPreferences()
        self.layout_preferences = LayoutPreferences()

        # First-time load from disk (if present), else create defaults
        if appdata.CATENA_PREFERENCES_PATH.exists():
            self.load()
        else:
            self.save()

    def to_dict(self) -> dict[str, appdata.JSON_TYPE]:
        """Serialize to a plain dict."""
        return {
            GENERAL_PREFERENCES: asdict(self.general_preferences),
            GRAPH_PREFERENCES: asdict(self.node_graph_preferences),
            LAYOUT_PREFERENCES: asdict(self.layout_preferences),
        }

    def from_dict(self, data: dict[str, appdata.JSON_TYPE]) -> None:
        """Apply a serialized dict into dataclass fields safely."""
        if GENERAL_PREFERENCES in data:
            self.general_preferences = GeneralPreferences(**data[GENERAL_PREFERENCES])
        if GRAPH_PREFERENCES in data:
            self.node_graph_preferences = NodeGraphPreferences(
                **data[GRAPH_PREFERENCES]
            )
        if LAYOUT_PREFERENCES in data:
            self.layout_preferences = LayoutPreferences(**data[LAYOUT_PREFERENCES])

    def load(self) -> None:
        """
        Load in data from user appdata file if it can be found, otherwise, save
        default data to user appdata folder.
        """
        data = io_utils.import_data_from_json(appdata.CATENA_PREFERENCES_PATH)
        if data is not None:
            self.from_dict(data)

    def save(self) -> None:
        """
        Save current data to user's appdata folder.
        Emit event signaling a potential update to preference data.
        Emitted data is None as the preference singleton can be accessed from
        anywhere.
        """
        io_utils.export_data_to_json(
            appdata.CATENA_PREFERENCES_PATH, self.to_dict(), True
        )
        broker.emit(namespace.PREFERENCES_UPDATED)


def initialize() -> None:
    """Call on startup to ensure the singletons are loaded."""
    _ = Preferences()
