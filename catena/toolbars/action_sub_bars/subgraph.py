from PySide6TK import QtWidgets
from PySide6TK import Resources

from catena.toolbars import actions
from catena.toolbars.action_sub_bars.base import ActionToolbar


class SubgraphToolbar(ActionToolbar):

    def __init__(self, parent: QtWidgets.QWidget) -> None:
        super().__init__("SubgraphToolbar", parent, Resources.BUTTON_BLACK_40X40)

    def build(self) -> None:
        self.add_action_button(
            "Sub\nGraph", actions.SubgraphActions.action_sub_graph_node
        )

        self.add_toolbar_separator(12)

        self.add_action_button("Input", actions.SubgraphActions.action_graph_input_node)
        self.add_action_button(
            "Output", actions.SubgraphActions.action_graph_output_node
        )
