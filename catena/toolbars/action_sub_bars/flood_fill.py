from PySide6TK import QtWidgets
from PySide6TK import Resources

from catena.nodes.graph_gui import GuiGraphView
from catena.toolbars import actions
from catena.toolbars.action_sub_bars.base import ActionToolbar


class FloodFillToolbar(ActionToolbar):

    def __init__(self, parent: QtWidgets.QWidget, graph_view: GuiGraphView) -> None:
        super().__init__(
            "FloodFillToolbar", parent, graph_view, Resources.BUTTON_MAGENTA_40X40
        )

    def build(self) -> None:
        self.add_action_button(
            "Flood\nFill", actions.FloodFillActions.action_flood_fill_node
        )

        self.add_toolbar_separator(12)

        self.add_action_button(
            "FF To\nGrad", actions.FloodFillActions.action_ff_to_gradient_node
        )
        self.add_action_button(
            "FF To\nGrey", actions.FloodFillActions.action_ff_to_greyscale_node
        )
        self.add_action_button(
            "FF To\nRand\nColor", actions.FloodFillActions.action_ff_to_rand_color_node
        )
