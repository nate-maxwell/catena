from PySide6TK import QtWidgets
from PySide6TK import QtWrappers
from PySide6TK import Resources

from catena.core.nodes.graph import CatenaGraphView
from catena.core.toolbars import actions


class TransformToolbar(QtWrappers.Toolbar):

    def __init__(self, parent: QtWidgets.QWidget, graph_view: CatenaGraphView) -> None:
        super().__init__(
            "Transform Toolbar", default_button_resolution=[40, 40], parent=parent
        )
        self.graph_view = graph_view

    def build(self) -> None:
        self.add_toolbar_command(
            "Flip",
            command=lambda: actions.XformActions.action_flip_node(self.graph_view),
            image_path=Resources.BUTTON_GREEN_40X40,
        )
        self.add_toolbar_command(
            "Offset",
            command=lambda: actions.XformActions.action_offset_node(self.graph_view),
            image_path=Resources.BUTTON_GREEN_40X40,
        )
        self.add_toolbar_command(
            "Rotate",
            command=lambda: actions.XformActions.action_rotate_node(self.graph_view),
            image_path=Resources.BUTTON_GREEN_40X40,
        )
        self.add_toolbar_command(
            "Tile",
            command=lambda: actions.XformActions.action_tile_node(self.graph_view),
            image_path=Resources.BUTTON_GREEN_40X40,
        )
