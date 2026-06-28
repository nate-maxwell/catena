"""
A record of which plugins the user has explicitly disabled.

Uses an opt-out model — all discovered plugins are enabled by default.
Only disabled plugins are persisted to disk. New plugins discovered after
the record was last saved are enabled automatically.
"""

import logging
from pathlib import Path
from typing import Any
from typing import Optional

import broker
import core_utils.structured

from catena import appdata
from catena import namespace

logger = logging.getLogger(__name__)


class PluginRecordData(object):
    """
    Singleton that persists the set of explicitly disabled plugin paths.

    All discovered plugins are enabled by default. Only paths the user
    has explicitly disabled are stored. This means new plugins discovered
    after the record was last saved are automatically enabled.
    """

    _instance: Optional["PluginRecordData"] = None

    def __new__(cls, *args: Any, **kwargs: Any) -> "PluginRecordData":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if getattr(self, "_initialized", False):
            return
        self._initialized = True

        self._disabled: set[str] = set()

        if appdata.CATENA_PLUGIN_RECORD_PATH.exists():
            self.load()
        else:
            self.save()

    def disabled_paths(self) -> set[str]:
        """
        Return the set of disabled plugin path strings.

        Returns:
            set[str]: Posix path strings of all disabled plugins.
        """
        return set(self._disabled)

    def is_enabled(self, path: Path) -> bool:
        """
        Return whether a plugin path is enabled.

        Args:
            path (Path): The plugin folder path.
        Returns:
            bool: True if the plugin is enabled.
        """
        return path.as_posix() not in self._disabled

    def set_disabled(self, path: Path, disabled: bool) -> None:
        """
        Mark a plugin path as disabled or re-enable it.

        Args:
            path (Path): The plugin folder path.
            disabled (bool): True to disable, False to re-enable.
        """
        key = path.as_posix()

        if disabled:
            self._disabled.add(key)
        else:
            self._disabled.discard(key)

    def to_dict(self) -> dict:
        """
        Serialize to a plain dict.

        Returns:
            dict: Serialized record data.
        """
        return {"disabled": sorted(self._disabled)}

    def from_dict(self, data: dict) -> None:
        """
        Apply a serialized dict into the record.

        Args:
            data (dict): Serialized record data.
        """
        self._disabled = set(data.get("disabled", []))

    def load(self) -> None:
        """Load the record from disk."""
        data = core_utils.structured.import_data_from_json(
            appdata.CATENA_PLUGIN_RECORD_PATH
        )

        if data is not None:
            self.from_dict(data)
            logger.info("Plugin record loaded")

    def save(self) -> None:
        """Persist the record to disk and notify subscribers."""
        core_utils.structured.export_data_to_json(
            appdata.CATENA_PLUGIN_RECORD_PATH, self.to_dict(), True
        )

        broker.emit(namespace.PLUGIN_DATA_UPDATED)
        logger.info("Plugin record saved")


def initialize() -> None:
    """Call on startup to ensure the singleton is loaded."""
    PluginRecordData()
    logger.info("Plugin record system initialized")
