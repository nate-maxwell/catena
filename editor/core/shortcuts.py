"""
# Shortcut Manager

Historically where I have used this class the class itself is a bucket for all
shortcuts and the functions they run, making one place to update all shortcut.

For Catena, systems themselves will register shortcuts by calling
catena.shortcuts.ShortcutManager().add_shortcut(...).
This allows modules to be added and removed more freely, and they will register
themselves with the shortcut manager.
"""
from typing import Optional

from PySide6 import QtWidgets
from PySide6TK import QtWrappers


def _null(*args) -> None:
    return


class ShortcutManager(QtWrappers.KeyShortcutManager):
    _instance: Optional["ShortcutManager"] = None

    def __new__(cls, parent: QtWidgets.QWidget) -> "ShortcutManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, parent: QtWidgets.QWidget) -> None:
        super().__init__(parent)


def init_shortcut_manager(parent: QtWidgets.QWidget) -> ShortcutManager:
    return ShortcutManager(parent)
