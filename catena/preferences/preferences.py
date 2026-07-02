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
from dataclasses import fields
from dataclasses import is_dataclass
from typing import Any
from typing import Optional
from typing import TypeVar

import broker
import core_utils.structured

from catena import appdata
from catena import namespace
from catena.preferences.category_data import GeneralPreferences
from catena.preferences.category_data import NodeGraphPreferences

logger = logging.getLogger(__name__)


class AppdataError(Exception):
    """Errors for unhandled appdata values."""


T = TypeVar("T")


def _safe_init(cls: type[T], data: dict[str, Any]) -> T:
    """
    Extract fields while logging warning about unknown fields.
    These fields are likely deprecated.
    """
    known = {f.name for f in fields(cls)}
    unknown = data.keys() - known
    if unknown:
        logger.warning(
            "Dropping unrecognized preference keys for %s: %s",
            cls.__name__,
            sorted(unknown),
        )

    return cls(**{k: v for k, v in data.items() if k in known})


def _ensure_dataclass_type(cls: type[T]):
    if not is_dataclass(cls):
        raise TypeError(f"{cls.__name__} must be a dataclass type.")


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
        # Prevent re-initialization on later calls
        if getattr(self, "_initialized", False):
            return
        self._initialized = True

        self._registered_types: dict[str, type[Any]] = {}
        self._sections: dict[str, Any] = {}
        self._serialized_data: dict[str, appdata.JSON_TYPE] = {}

        # Defaults
        self.register_section("general_preferences", GeneralPreferences)
        self.register_section("node_graph_preferences", NodeGraphPreferences)

        # First-time load from disk (if present), else file defaults
        if appdata.CATENA_PREFERENCES_PATH.exists():
            self.load()
        else:
            self.save()

    def _create_section(self, key: str, cls: type[T]) -> T:
        data = self._serialized_data.get(key)
        if isinstance(data, dict):
            return _safe_init(cls, data)

        if data is not None:
            logger.warning(
                "Dropping malformed preference data for %s: expected object, got %s",
                key,
                type(data).__name__,
            )

        return cls()

    def register_section(self, key: str, cls: type[T]) -> T:
        """
        Register a dataclass-backed preference object under a persistent key.

        If the current preferences snapshot already contains data for the key,
        that data is used to populate the new object. Otherwise, the dataclass
        defaults are used.
        """
        _ensure_dataclass_type(cls)
        if key in self._registered_types:
            raise ValueError(f"Preference section {key!r} is already registered.")

        value = self._create_section(key, cls)
        self._registered_types[key] = cls
        self._sections[key] = value
        return value

    def __getitem__(self, key: str) -> Any:
        if key not in self._registered_types:
            raise KeyError(f"Preference section {key!r} is not registered.")

        return self._sections[key]

    def __setitem__(self, key: str, value: Any) -> None:
        if key not in self._registered_types:
            raise KeyError(f"Preference section {key!r} is not registered.")

        expected_type = self._registered_types[key]
        if not isinstance(value, expected_type):
            raise TypeError(
                f"Preference section {key!r} must be assigned {expected_type.__name__}."
            )

        self._sections[key] = value

    def get_section(self, key: str) -> Any:
        """Return a previously registered preference object."""
        return self[key]

    def registered_keys(self) -> tuple[str, ...]:
        """Return the persistent keys currently managed by the singleton."""
        return tuple(self._registered_types.keys())

    def to_dict(self) -> dict[str, appdata.JSON_TYPE]:
        """Serialize to a plain dict."""
        data = dict(self._serialized_data)
        for key, value in self._sections.items():
            data[key] = asdict(value)

        return data

    def from_dict(self, data: dict[str, appdata.JSON_TYPE]) -> None:
        """Apply a serialized dict into dataclass fields safely."""
        self._serialized_data = dict(data)
        for key, cls in self._registered_types.items():
            if key in data:
                self._sections[key] = _create_from_data(cls, data[key])

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


def _create_from_data(cls: type[T], value: appdata.JSON_TYPE) -> T:
    if isinstance(value, dict):
        return _safe_init(cls, value)

    logger.warning(
        "Dropping malformed preference data for %s: expected object, got %s",
        cls.__name__,
        type(value).__name__,
    )

    return cls()


def initialize() -> None:
    """Call on startup to ensure the singleton is loaded."""
    Preferences()
    logger.info("Preferences system initialized")
