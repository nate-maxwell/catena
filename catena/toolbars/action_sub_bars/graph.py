from PySide6TK import QtWidgets
from PySide6TK import Resources

from catena.toolbars import actions
from catena.toolbars.action_sub_bars.base import ActionToolbar


class GraphToolbar(ActionToolbar):

    def __init__(self, parent: QtWidgets.QWidget) -> None:
        super().__init__("GraphToolbar", parent, Resources.BUTTON_BLACK_40X40)

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

        self.add_toolbar_separator(12)

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
