from PySide6TK import QtWidgets
from PySide6TK import Resources

from catena.toolbars import actions
from catena.toolbars.action_sub_bars.base import ActionToolbar


class ModifierToolbar(ActionToolbar):

    def __init__(self, parent: QtWidgets.QWidget) -> None:
        super().__init__("ModifierToolbar", parent, Resources.BUTTON_YELLOW_40X40)

    def build(self) -> None:
        self.add_action_button("Bevel", actions.ModifierActions.action_bevel_node)
        self.add_action_button("Blur", actions.ModifierActions.action_blur_node)
        self.add_action_button("Contrst", actions.ModifierActions.action_contrast_node)
        self.add_action_button(
            "Edge\nDetect", actions.ModifierActions.action_edge_detect_node
        )
        self.add_action_button("Histo", actions.ModifierActions.action_historgram_node)
        self.add_action_button("HSV", actions.ModifierActions.action_hsv_node)
        self.add_action_button("Invert", actions.ModifierActions.action_invert_node)
        self.add_action_button("Levels", actions.ModifierActions.action_levels_node)
        self.add_action_button("Nrmlize", actions.ModifierActions.action_normalize_node)
        self.add_action_button("Overlay", actions.ModifierActions.action_overlay_node)
        self.add_action_button("Sharpen", actions.ModifierActions.action_sharpen_node)
        self.add_action_button(
            "Slope\nBlur", actions.ModifierActions.action_slope_blur_node
        )
        self.add_action_button("Thresh", actions.ModifierActions.action_threshold_node)
