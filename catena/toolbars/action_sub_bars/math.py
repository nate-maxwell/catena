from PySide6TK import QtWidgets
from PySide6TK import Resources

from catena.nodes.graph_gui import GuiGraphView
from catena.toolbars import actions
from catena.toolbars.action_sub_bars.base import ActionToolbar


class MathToolbar(ActionToolbar):

    def __init__(self, parent: QtWidgets.QWidget, graph_view: GuiGraphView) -> None:
        super().__init__("MathToolbar", parent, graph_view, Resources.BUTTON_CYAN_40X40)

    def build(self) -> None:
        self.add_action_button("Add", actions.MathActions.action_add_node)
        self.add_action_button("Sub", actions.MathActions.action_subtract_node)
        self.add_action_button("Mul", actions.MathActions.action_multiply_node)
        self.add_action_button("Div", actions.MathActions.action_divide_node)

        self.add_toolbar_separator(12)

        self.add_action_button("Min", actions.MathActions.action_min_node)
        self.add_action_button("Max", actions.MathActions.action_max_node)

        self.add_toolbar_separator(12)

        self.add_action_button("Screen", actions.MathActions.action_screen_node)

        self.add_toolbar_separator(12)

        self.add_action_button("Sin", actions.MathActions.action_sin_node)
        self.add_action_button("Cosin", actions.MathActions.action_cosin_node)
        self.add_action_button("Tan", actions.MathActions.action_tan_node)
        self.add_action_button("Arctan", actions.MathActions.action_arctan_node)
