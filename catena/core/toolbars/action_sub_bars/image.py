from PySide6TK import QtWidgets
from PySide6TK import QtWrappers
from PySide6TK import Resources

from catena.core.nodes.graph import CatenaGraphView
from catena.core.toolbars import actions


class ImageToolbar(QtWrappers.Toolbar):

    def __init__(self, parent: QtWidgets.QWidget, graph_view: CatenaGraphView) -> None:
        super().__init__(
            "Image Toolbar", default_button_resolution=[40, 40], parent=parent
        )
        self.graph_view = graph_view

    def build(self) -> None:
        self.add_toolbar_command(
            "Blur",
            command=lambda: actions.ImageActions.action_blur_node(self.graph_view),
            image_path=Resources.BUTTON_YELLOW_40X40,
        )
        self.add_toolbar_command(
            "Contrst",
            command=lambda: actions.ImageActions.action_contrast_node(self.graph_view),
            image_path=Resources.BUTTON_YELLOW_40X40,
        )
        self.add_toolbar_command(
            "Color",
            command=lambda: actions.ImageActions.action_threshold_node(self.graph_view),
            image_path=Resources.BUTTON_YELLOW_40X40,
        )
        self.add_toolbar_command(
            "HSV",
            command=lambda: actions.ImageActions.action_hsv_node(self.graph_view),
            image_path=Resources.BUTTON_YELLOW_40X40,
        )
        self.add_toolbar_command(
            "Invert",
            command=lambda: actions.ImageActions.action_invert_node(self.graph_view),
            image_path=Resources.BUTTON_YELLOW_40X40,
        )
        self.add_toolbar_command(
            "Levels",
            command=lambda: actions.ImageActions.action_levels_node(self.graph_view),
            image_path=Resources.BUTTON_YELLOW_40X40,
        )
        self.add_toolbar_command(
            "Overlay",
            command=lambda: actions.ImageActions.action_overlay_node(self.graph_view),
            image_path=Resources.BUTTON_YELLOW_40X40,
        )
        self.add_toolbar_command(
            "Sharpen",
            command=lambda: actions.ImageActions.action_sharpen_node(self.graph_view),
            image_path=Resources.BUTTON_YELLOW_40X40,
        )
        self.add_toolbar_command(
            "Thresh",
            command=lambda: actions.ImageActions.action_threshold_node(self.graph_view),
            image_path=Resources.BUTTON_YELLOW_40X40,
        )
        self.add_toolbar_command(
            "Warp",
            command=lambda: actions.ImageActions.action_warp_node(self.graph_view),
            image_path=Resources.BUTTON_YELLOW_40X40,
        )
