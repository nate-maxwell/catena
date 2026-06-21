from PySide6TK import QtWidgets
from PySide6TK import Resources

from catena.nodes.graph_gui import GuiGraphView
from catena.toolbars import actions
from catena.toolbars.action_sub_bars.base import ActionToolbar


class ImageToolbar(ActionToolbar):

    def __init__(self, parent: QtWidgets.QWidget, graph_view: GuiGraphView) -> None:
        super().__init__(
            "ImageToolbar", parent, graph_view, Resources.BUTTON_YELLOW_40X40
        )

    def build(self) -> None:
        self.add_action_button("Bevel", actions.ImageActions.action_bevel_node)
        self.add_action_button("Blur", actions.ImageActions.action_blur_node)
        self.add_action_button("Contrst", actions.ImageActions.action_contrast_node)
        self.add_action_button("Histo", actions.ImageActions.action_historgram_node)
        self.add_action_button("Color", actions.ImageActions.action_color_node)
        self.add_action_button("HSV", actions.ImageActions.action_hsv_node)
        self.add_action_button("Invert", actions.ImageActions.action_invert_node)
        self.add_action_button("Levels", actions.ImageActions.action_levels_node)
        self.add_action_button("Nrmlize", actions.ImageActions.action_normalize_node)
        self.add_action_button("Overlay", actions.ImageActions.action_overlay_node)
        self.add_action_button("Sharpen", actions.ImageActions.action_sharpen_node)
        self.add_action_button(
            "Slope\nBlur", actions.ImageActions.action_slope_blur_node
        )
        self.add_action_button("Thresh", actions.ImageActions.action_threshold_node)
        self.add_action_button("Warp", actions.ImageActions.action_warp_node)
