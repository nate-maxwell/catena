from __future__ import annotations

from typing import TYPE_CHECKING

import broker
from PySide6 import QtWidgets
from PySide6TK import QtWrappers

from catena.components.about import about
from catena.core import shortcuts
from catena.core import namespace
from catena.components.preferences import menu as preferences_menu

if TYPE_CHECKING:
    from catena.core.client import CatenaEditor


class ClientWindowToolbar(QtWrappers.Toolbar):
    def __init__(self, parent: CatenaEditor) -> None:
        self._editor = parent
        super().__init__("EditorClientToolbar", parent)
        self.setMinimumHeight(22)
        self.setMaximumHeight(26)
        self.setStyleSheet("""
            QToolButton::menu-indicator {
                image: none;
                width: 0px;
            }
        """)

    def build(self) -> None:
        self._file_section()
        self._edit_section()
        self._view_section()
        self._help_section()

    def _file_section(self) -> None:
        menu = self.add_menu("File")
        self.add_menu_command(menu, "New File")
        self.add_menu_command(
            menu, "Open File", lambda: broker.emit(namespace.CLIENT_LOAD)
        )
        self.add_menu_command(
            menu, "Save File", lambda: broker.emit(namespace.CLIENT_SAVE)
        )
        self.add_menu_command(
            menu, "Save As", lambda: broker.emit(namespace.CLIENT_SAVE_AS)
        )
        self.add_menu_command(menu, "Quit", QtWidgets.QApplication.quit)

    def _edit_section(self) -> None:
        manager = shortcuts.init_shortcut_manager(self.parent())

        menu = self.add_menu("Edit")
        self.add_menu_command(menu, "Undo", lambda: broker.emit(namespace.CLIENT_UNDO))
        self.add_menu_command(menu, "Redo", lambda: broker.emit(namespace.CLIENT_REDO))
        self.add_menu_command(menu, "Shortcuts", manager.show_editor)
        self.add_menu_command(
            menu,
            "Settings",
            lambda: preferences_menu.show_preferences_widget(self.parent()),
        )

    def _view_section(self) -> None:
        menu = self.add_menu("View")
        self.add_menu_command(
            menu, "Viewport", self._editor.pane_viewport.toggle_visibility
        )
        self.add_menu_command(
            menu, "Node Graph", self._editor.pane_graph.toggle_visibility
        )
        self.add_menu_command(
            menu,
            "Properties",
            self._editor.pane_properties.toggle_visibility,
        )

    def _help_section(self) -> None:
        menu = self.add_menu("Help")
        self.add_menu_command(menu, "About", lambda: about.show_about_widget(self))
