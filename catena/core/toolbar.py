from PySide6 import QtWidgets
from PySide6TK import QtWrappers

from catena.core import about
from catena.core import shortcuts


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
        self.add_menu_command(menu, "Save")
        self.add_menu_command(menu, "Save All")
        self.add_menu_command(menu, "Quit")

    def _edit_section(self) -> None:
        manager = shortcuts.init_shortcut_manager(self.parent())

        menu = self.add_menu("Edit")
        self.add_menu_command(menu, "Undo")
        self.add_menu_command(menu, "Redo")
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


class EditorActionToolbar(QtWrappers.Toolbar):

    def __init__(self) -> None:
        super().__init__("Example Toolbar", default_button_resolution=[40, 40])

    def build(self) -> None:
        self._action_queue_section()
        self.add_toolbar_separator()
        self._create_section()
        self.add_toolbar_separator()
        self._play_section()
        self.add_toolbar_separator()

    def _action_queue_section(self) -> None:
        self.add_toolbar_command("Save", image_path=QtWrappers.BUTTON_CYAN_40X40)
        self.add_toolbar_command("Undo", image_path=QtWrappers.BUTTON_ORANGE_40X40)
        self.add_toolbar_command("Redo", image_path=QtWrappers.BUTTON_ORANGE_40X40)

    def _create_section(self) -> None:
        self.add_toolbar_command(
            "Create\nPanel", image_path=QtWrappers.BUTTON_BLUE_40X40
        )
        self.add_toolbar_command(
            "Create\nVariant", image_path=QtWrappers.BUTTON_BLUE_40X40
        )
        self.add_toolbar_command("Import", image_path=QtWrappers.BUTTON_YELLOW_40X40)

    def _play_section(self) -> None:
        self.add_toolbar_command("Play", image_path=QtWrappers.BUTTON_GREEN_40X40)
        self.add_toolbar_command("Stop", image_path=QtWrappers.BUTTON_RED_40X40)
