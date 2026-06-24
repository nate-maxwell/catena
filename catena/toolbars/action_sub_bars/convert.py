from PySide6TK import QtWidgets
from PySide6TK import Resources

from catena.nodes.graph_gui import GuiGraphView
from catena.toolbars import actions
from catena.toolbars.action_sub_bars.base import ActionToolbar


class ConvertToolbar(ActionToolbar):

    def __init__(self, parent: QtWidgets.QWidget) -> None:
        super().__init__("ConvertToolbar", parent, Resources.BUTTON_BLUE_40X40)

    def build(self) -> None:
        self.add_action_button("Split", actions.ConvertActions.action_split_node)
        self.add_action_button("Append", actions.ConvertActions.action_append_node)

        self.add_toolbar_separator(12)

        self.add_action_button("H2AO", actions.ConvertActions.action_h2ao_node)
        self.add_action_button("H2N", actions.ConvertActions.action_h2m_node)

        self.add_toolbar_separator(12)

        self.add_action_button(
            "Int\nto\nFloat", actions.ConvertActions.action_int_to_float_node
        )
        self.add_action_button(
            "Int\nto\nVec4", actions.ConvertActions.action_int_to_vec4_node
        )
        self.add_action_button(
            "Float\nto\nInt", actions.ConvertActions.action_float_to_int_node
        )
        self.add_action_button(
            "Float\nto\nVec4", actions.ConvertActions.action_float_to_vec4_node
        )
