from typing import Optional

from PySide6 import QtWidgets
from PySide6TK import QtWrappers


def _null(*args) -> None:
    return


class ShortcutManager(QtWrappers.KeyShortcutManager):
    def __init__(self, parent: QtWidgets.QWidget) -> None:
        super().__init__(parent)

        self._create_shortcuts()

    def _create_shortcuts(self) -> None:
        self.add_shortcut(
            "save_file",
            "Ctrl+S",
            _null,
            "Save the current file.",
            "File",
        )
        self.add_shortcut(
            "save_all",
            "Ctrl+Shift+S",
            _null,
            "Save all current files.",
            "File",
        )
        self.add_shortcut(
            "open_project",
            "Ctrl+Shift+O",
            _null,
            "Open a project.",
            "File",
        )
        self.add_shortcut(
            "run_code",
            "Ctrl+Return",
            _null,
            "Run active tab code.",
            "Code",
        )
        self.add_shortcut(
            "run_code_alt",
            "Ctrl+Enter",
            _null,
            "Run active tab code.",
            "Code",
        )
        self.add_shortcut(
            "open_terminal",
            "Ctrl+`",
            _null,
            "Show the terminal.",
            "Code",
        )
        self.add_shortcut(
            "toggle_full_screen",
            "F11",
            _null,
            "Toggle fullscreen",
            "UI",
        )


_shortcut_manager: Optional[ShortcutManager] = None


def init_shortcut_manager(parent: QtWidgets.QWidget) -> ShortcutManager:
    global _shortcut_manager
    if _shortcut_manager is None:
        _shortcut_manager = ShortcutManager(parent)

    return _shortcut_manager
