from PySide6TK import QtWidgets
from PySide6TK import Resources

from catena.nodes.graph_gui import GuiGraphView
from catena.toolbars import actions
from catena.toolbars.action_sub_bars.base import ActionToolbar


class GeneratorToolbar(ActionToolbar):

    def __init__(self, parent: QtWidgets.QWidget, graph_view: GuiGraphView) -> None:
        super().__init__(
            "GeneratorToolbar", parent, graph_view, Resources.BUTTON_PURPLE_40X40
        )

    def build(self) -> None:
        self.add_action_button(
            "Blue\nNoise", actions.GeneratorActions.action_blue_noise_node
        )
        self.add_action_button(
            "BnW\nSpots", actions.GeneratorActions.action_bnw_spots_node
        )
        self.add_action_button("Cells", actions.GeneratorActions.action_cells_node)
        self.add_action_button("Clouds", actions.GeneratorActions.action_clouds_node)
        self.add_action_button("Fibers", actions.GeneratorActions.action_fibers_node)
        self.add_action_button(
            "Perlin\nNoise", actions.GeneratorActions.action_perlin_noise_node
        )
        self.add_action_button(
            "White\nNoise", actions.GeneratorActions.action_white_noise_node
        )
        self.add_action_button(
            "Voronoi", actions.GeneratorActions.action_voronoi_noise_node
        )

        self.add_toolbar_separator(12)

        self.add_action_button("Color", actions.GeneratorActions.action_color_node)
        self.add_action_button("Grad", actions.GeneratorActions.action_gradient_node)
        self.add_action_button("Checker", actions.GeneratorActions.action_checker_node)
        self.add_action_button("Poly", actions.GeneratorActions.action_polygon_node)
        self.add_action_button("Shape", actions.GeneratorActions.action_shape_node)

        self.add_toolbar_separator(12)

        self.add_action_button(
            "Grunge", actions.GeneratorActions.action_grunge_one_node
        )
        self.add_action_button("Mold", actions.GeneratorActions.action_mold_node)

        self.add_toolbar_separator(12)

        self.add_action_button(
            "Scratch", actions.GeneratorActions.action_scratches_node
        )
        self.add_action_button("Weave", actions.GeneratorActions.action_weave_node)
