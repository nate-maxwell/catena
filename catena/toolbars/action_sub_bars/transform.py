from PySide6TK import QtWidgets
from PySide6TK import Resources

from catena.nodes.graph_gui import GuiGraphView
from catena.toolbars import actions
from catena.toolbars.action_sub_bars.base import ActionToolbar


class TransformToolbar(ActionToolbar):

    def __init__(self, parent: QtWidgets.QWidget, graph_view: GuiGraphView) -> None:
        super().__init__(
            "TransformToolbar", parent, graph_view, Resources.BUTTON_GREEN_40X40
        )

    def build(self) -> None:
        self.add_action_button("Flip", actions.XformActions.action_flip_node)
        self.add_action_button("Offset", actions.XformActions.action_offset_node)
        self.add_action_button("Rotate", actions.XformActions.action_rotate_node)
        self.add_action_button("Scatter", actions.XformActions.action_scatter_node)
        self.add_action_button("Tile", actions.XformActions.action_tile_node)
