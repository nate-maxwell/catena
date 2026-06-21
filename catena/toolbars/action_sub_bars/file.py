from PySide6TK import QtWidgets
from PySide6TK import Resources

from catena.nodes.graph_gui import GuiGraphView
from catena.toolbars import actions
from catena.toolbars.action_sub_bars.base import ActionToolbar


class CreateToolbar(ActionToolbar):

    def __init__(self, parent: QtWidgets.QWidget, graph_view: GuiGraphView) -> None:
        super().__init__("FileToolbar", parent, graph_view, Resources.BUTTON_RED_40X40)

    def build(self) -> None:
        self.add_action_button("Read", actions.CreateActions.action_read_node)

        self.add_toolbar_separator(12)

        self.add_action_button(
            "Write\nAlbedo", actions.CreateActions.action_albedo_node
        )
        self.add_action_button("Write\nAO", actions.CreateActions.action_ao_node)
        self.add_action_button(
            "Write\nHeight", actions.CreateActions.action_height_node
        )
        self.add_action_button(
            "Write\nMetallic", actions.CreateActions.action_metallic_node
        )
        self.add_action_button(
            "Write\nNormal", actions.CreateActions.action_normal_node
        )
        self.add_action_button(
            "Write\nRough", actions.CreateActions.action_roughness_node
        )
