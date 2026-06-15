from PySide6TK import QtWidgets
from PySide6TK import QtWrappers
from PySide6TK import Resources

from catena.core.nodes.graph import CatenaGraphView
from catena.core.toolbars import actions


class CreateToolbar(QtWrappers.Toolbar):

    def __init__(self, parent: QtWidgets.QWidget, graph_view: CatenaGraphView) -> None:
        super().__init__(
            "FileToolbar", default_button_resolution=[40, 40], parent=parent
        )
        self.graph_view = graph_view

    def build(self) -> None:
        self.add_toolbar_command(
            "Read",
            command=lambda: actions.CreateActions.action_read_node(self.graph_view),
            image_path=Resources.BUTTON_RED_40X40,
        )

        self.add_toolbar_separator(12)

        self.add_toolbar_command(
            "Albedo",
            command=lambda: actions.CreateActions.action_albedo_node(self.graph_view),
            image_path=Resources.BUTTON_RED_40X40,
        )
        self.add_toolbar_command(
            "Write\nAO",
            command=lambda: actions.CreateActions.action_ao_node(self.graph_view),
            image_path=Resources.BUTTON_RED_40X40,
        )
        self.add_toolbar_command(
            "Write\nHeight",
            command=lambda: actions.CreateActions.action_height_node(self.graph_view),
            image_path=Resources.BUTTON_RED_40X40,
        )
        self.add_toolbar_command(
            "Write\nMetallic",
            command=lambda: actions.CreateActions.action_metallic_node(self.graph_view),
            image_path=Resources.BUTTON_RED_40X40,
        )
        self.add_toolbar_command(
            "Write\nNormal",
            command=lambda: actions.CreateActions.action_normal_node(self.graph_view),
            image_path=Resources.BUTTON_RED_40X40,
        )
        self.add_toolbar_command(
            "Write\nRough",
            command=lambda: actions.CreateActions.action_roughness_node(
                self.graph_view
            ),
            image_path=Resources.BUTTON_RED_40X40,
        )
