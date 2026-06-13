from PySide6TK import QtWidgets
from PySide6TK import QtWrappers
from PySide6TK import Resources

from catena.core.nodes.graph import CatenaGraphView
from catena.core.toolbars import actions


class FileToolbar(QtWrappers.Toolbar):

    def __init__(self, parent: QtWidgets.QWidget, graph_view: CatenaGraphView) -> None:
        super().__init__(
            "File Toolbar", default_button_resolution=[40, 40], parent=parent
        )
        self.graph_view = graph_view

    def build(self) -> None:
        self.add_toolbar_command(
            "Save",
            command=lambda: actions.ClientActions.action_save(),
            image_path=Resources.BUTTON_BLACK_40X40,
        )
        self.add_toolbar_command(
            "Pub\nFiles",
            command=lambda: actions.ClientActions.action_write_files(),
            image_path=Resources.BUTTON_BLACK_40X40,
        )
        self.add_toolbar_command(
            "Undo",
            command=lambda: actions.ClientActions.action_undo(),
            image_path=Resources.BUTTON_BLACK_40X40,
        )
        self.add_toolbar_command(
            "Redo",
            command=lambda: actions.ClientActions.action_redo(),
            image_path=Resources.BUTTON_BLACK_40X40,
        )
