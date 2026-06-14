"""
# Session Data

* Description:

    Singleton container for runtime session state in Catena, such as the
    currently opened project file, backed by a JSON file in roaming appdata.
    Loaded on first access and persisted via ``save``. Emits
    ``namespace.SESSION_DATA_UPDATED`` whenever session data is saved, so
    other parts of the application can react to changes without needing a
    direct reference to this singleton.
"""

from pathlib import Path
from typing import Any
from typing import Optional

import broker

from catena.core import appdata
from catena.core import io_utils
from catena.core import namespace

_PROJECT_FILE = "project_file"


class SessionData(object):
    """
    Singleton container holding all session specific values.

    Values such as the current opened directory, or other things necessary for
    the client to function.
    """

    _instance: Optional["SessionData"] = None

    def __new__(cls, *args: Any, **kwargs: Any) -> "SessionData":
        if cls._instance is None:
            cls._instance = super(SessionData, cls).__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        # Prevent re-initialization on subsequent calls
        if getattr(self, "_initialized", False):
            return
        self._initialized = True

        # -----Data-----
        self.project_file = appdata.INITIAL_CATENA_FILE

        # First-time load from disk (if present), else create defaults
        if appdata.CATENA_SESSION_DATA_PATH.exists():
            self.load()
        else:
            self.save()

    def to_dict(self) -> dict[str, appdata.JSON_TYPE]:
        """Serialize to a plain dict."""
        return {_PROJECT_FILE: self.project_file.as_posix()}

    def from_dict(self, data: dict[str, appdata.JSON_TYPE]) -> None:
        """Apply a serialized dict into dataclass fields safely."""
        self.project_file = Path(data.get(_PROJECT_FILE, self.project_file))

    def load(self) -> None:
        """
        Load in data from user appdata file if it can be found, otherwise, save
        default data to user appdata folder.
        """
        data = io_utils.import_data_from_json(appdata.CATENA_SESSION_DATA_PATH)
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
            appdata.CATENA_SESSION_DATA_PATH, self.to_dict(), True
        )
        broker.emit(namespace.SESSION_DATA_UPDATED)


def initialize() -> None:
    """Call on startup to ensure the singletons are loaded."""
    _ = SessionData()
