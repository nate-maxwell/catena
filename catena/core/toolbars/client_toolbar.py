import broker
from PySide6 import QtWidgets
from PySide6TK import QtWrappers

from catena.components import about
from catena.core import shortcuts
from catena.core import namespace


class ClientWindowToolbar(QtWrappers.Toolbar):
    def __init__(self, parent: QtWidgets.QWidget) -> None:
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
        self.add_menu_command(menu, "New Project")
        self.add_menu_command(menu, "Open Project")
        self.add_menu_command(menu, "Save", lambda: broker.emit(namespace.CLIENT_SAVE))
        self.add_menu_command(menu, "Quit", QtWidgets.QApplication.quit)

    def _edit_section(self) -> None:
        manager = shortcuts.init_shortcut_manager(self.parent())

        menu = self.add_menu("Edit")
        self.add_menu_command(menu, "Undo", lambda: broker.emit(namespace.CLIENT_UNDO))
        self.add_menu_command(menu, "Redo", lambda: broker.emit(namespace.CLIENT_REDO))
        self.add_menu_command(menu, "Shortcuts", manager.show_editor)
        self.add_menu_command(menu, "Editor Settings")

    def _view_section(self) -> None:
        menu = self.add_menu("View")
        self.add_menu_command(menu, "Open Viewport")
        self.add_menu_command(menu, "Open Content Browser")
        self.add_menu_command(menu, "Open Outliner")
        self.add_menu_command(menu, "Open Properties Panel")

    def _help_section(self) -> None:
        menu = self.add_menu("Help")
        self.add_menu_command(menu, "About", lambda: about.show_about_widget(self))
