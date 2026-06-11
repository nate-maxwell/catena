from PySide6TK import QtWidgets
from PySide6TK import QtWrappers
from PySide6TK import Resources

from catena.core.toolbars import actions
from catena.core.nodes.graph import CatenaGraphView


class EditorActionToolbar(QtWrappers.Toolbar):

    def __init__(self, parent: QtWidgets.QWidget, graph_view: CatenaGraphView) -> None:
        super().__init__(
            "Example Toolbar", default_button_resolution=[40, 40], parent=parent
        )
        self.graph_view = graph_view

    def build(self) -> None:
        self._action_queue_section()
        self.add_toolbar_separator()
        self._sequence_section()
        self.add_toolbar_separator()
        self._image_edit_section()

    def _action_queue_section(self) -> None:
        self.add_toolbar_command("Save", image_path=Resources.BUTTON_BLACK_40X40)
        self.add_toolbar_command("Undo", image_path=Resources.BUTTON_BLACK_40X40)
        self.add_toolbar_command("Redo", image_path=Resources.BUTTON_BLACK_40X40)

    def _sequence_section(self) -> None:
        self.add_toolbar_command(
            "Panel",
            command=lambda: actions.action_panel_node(self.graph_view),
            image_path=Resources.BUTTON_GREEN_40X40,
        )
        self.add_toolbar_command(
            "Start",
            command=lambda: actions.action_start_node(self.graph_view),
            image_path=Resources.BUTTON_RED_40X40,
        )
        self.add_toolbar_command(
            "Trans",
            command=lambda: actions.action_trans_node(self.graph_view),
            image_path=Resources.BUTTON_PURPLE_40X40,
        )
        self.add_toolbar_command(
            "Outro",
            command=lambda: actions.action_outro_node(self.graph_view),
            image_path=Resources.BUTTON_CYAN_40X40,
        )

    def _image_edit_section(self) -> None:
        self.add_toolbar_command("Overlay", image_path=Resources.BUTTON_YELLOW_40X40)
        self.add_toolbar_command(
            "Color\nGrade", image_path=Resources.BUTTON_YELLOW_40X40
        )
        self.add_toolbar_command("Crop", image_path=Resources.BUTTON_YELLOW_40X40)
        self.add_toolbar_command("Zoom", image_path=Resources.BUTTON_YELLOW_40X40)
        self.add_toolbar_command(
            "Water\nMark", image_path=Resources.BUTTON_YELLOW_40X40
        )
