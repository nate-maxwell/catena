"""
# Preferences

* Description:

    Singleton preferences container for Catena, backed by a JSON file in
    roaming appdata. Holds general, node graph, and layout preference
    dataclasses, loading them from disk on first access and persisting
    changes via ``save``. Emits ``namespace.PREFERENCES_UPDATED`` whenever
    preferences are saved, so other parts of the application can react to
    changes without needing a direct reference to this singleton.
"""

import logging
from dataclasses import asdict
from typing import Any
from typing import Optional

import broker
import core_utils.structured

from catena import appdata
from catena import namespace
from catena.preferences.category_data import GeneralPreferences
from catena.preferences.category_data import LayoutPreferences
from catena.preferences.category_data import NodeGraphPreferences

logger = logging.getLogger(__name__)

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

        # First-time load from disk (if present), else file defaults
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
        data = core_utils.structured.import_data_from_json(
            appdata.CATENA_PREFERENCES_PATH
        )
        if data is not None:
            self.from_dict(data)
            logger.info("Preferences loaded")

    def save(self) -> None:
        """
        Save current data to user's appdata folder.
        Emit event signaling a potential update to preference data.
        Emitted data is None as the preference singleton can be accessed from
        anywhere.
        """
        core_utils.structured.export_data_to_json(
            appdata.CATENA_PREFERENCES_PATH, self.to_dict(), True
        )
        broker.emit(namespace.PREFERENCES_UPDATED)
        logger.info("Preferences saved")


def initialize() -> None:
    """Call on startup to ensure the singletons are loaded."""
    _ = Preferences()
    logger.info("Preferences system initialized")
