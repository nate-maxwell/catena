from PySide6TK import QtWidgets
from PySide6TK import QtWrappers
from PySide6TK import Resources

from catena.core.nodes.graph import CatenaGraphView
from catena.core.toolbars import actions


class GeneratorToolbar(QtWrappers.Toolbar):

    def __init__(self, parent: QtWidgets.QWidget, graph_view: CatenaGraphView) -> None:
        super().__init__(
            "Generator Toolbar", default_button_resolution=[40, 40], parent=parent
        )
        self.graph_view = graph_view

    def build(self) -> None:
        self.add_toolbar_command(
            "Blue\nNoise",
            command=lambda: actions.GeneratorActions.action_blue_noise_node(
                self.graph_view
            ),
            image_path=Resources.BUTTON_PURPLE_40X40,
        )
        self.add_toolbar_command(
            "BnW\nSpots",
            command=lambda: actions.GeneratorActions.action_bnw_spots_node(
                self.graph_view
            ),
            image_path=Resources.BUTTON_PURPLE_40X40,
        )
        self.add_toolbar_command(
            "Cells",
            command=lambda: actions.GeneratorActions.action_cells_node(self.graph_view),
            image_path=Resources.BUTTON_PURPLE_40X40,
        )
        self.add_toolbar_command(
            "Clouds",
            command=lambda: actions.GeneratorActions.action_clouds_node(
                self.graph_view
            ),
            image_path=Resources.BUTTON_PURPLE_40X40,
        )
        self.add_toolbar_command(
            "Grad",
            command=lambda: actions.GeneratorActions.action_gradient_node(
                self.graph_view
            ),
            image_path=Resources.BUTTON_PURPLE_40X40,
        )
        self.add_toolbar_command(
            "Perlin\nNoise",
            command=lambda: actions.GeneratorActions.action_perlin_noise_node(
                self.graph_view
            ),
            image_path=Resources.BUTTON_PURPLE_40X40,
        )
        self.add_toolbar_command(
            "Shape",
            command=lambda: actions.GeneratorActions.action_shape_node(self.graph_view),
            image_path=Resources.BUTTON_PURPLE_40X40,
        )
        self.add_toolbar_command(
            "White\nNoise",
            command=lambda: actions.GeneratorActions.action_white_noise_node(
                self.graph_view
            ),
            image_path=Resources.BUTTON_PURPLE_40X40,
        )
