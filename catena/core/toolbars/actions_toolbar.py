from PySide6TK import QtWidgets
from PySide6TK import QtWrappers
from PySide6TK import Resources

from catena.core.nodes.graph import CatenaGraphView
from catena.core.toolbars import actions


class EditorActionToolbar(QtWrappers.Toolbar):

    def __init__(self, parent: QtWidgets.QWidget, graph_view: CatenaGraphView) -> None:
        super().__init__(
            "Example Toolbar", default_button_resolution=[40, 40], parent=parent
        )
        self.graph_view = graph_view

    def build(self) -> None:
        self._action_queue_section()
        self.add_toolbar_separator()
        self._create_section()
        self.add_toolbar_separator()
        self._image_section()
        self.add_toolbar_separator()
        self._transform_section()
        self.add_toolbar_separator()
        self._math_section()

    def _action_queue_section(self) -> None:
        self.add_toolbar_command(
            "Save",
            command=lambda: actions.ClientActions.action_save(),
            image_path=Resources.BUTTON_BLACK_40X40,
        )
        self.add_toolbar_command(
            "Undo",
            command=lambda: actions.ClientActions.action_undo(),
            image_path=Resources.BUTTON_BLACK_40X40,
        )
        self.add_toolbar_command(
            "Redo",
            command=lambda: actions.ClientActions.action_redo(),
            image_path=Resources.BUTTON_BLACK_40X40,
        )

    def _create_section(self) -> None:
        self.add_toolbar_command(
            "Panel",
            command=lambda: actions.CreateActions.action_panel_node(self.graph_view),
            image_path=Resources.BUTTON_GREEN_40X40,
        )
        self.add_toolbar_command(
            "Start",
            command=lambda: actions.CreateActions.action_start_node(self.graph_view),
            image_path=Resources.BUTTON_RED_40X40,
        )
        self.add_toolbar_command(
            "Trans",
            command=lambda: actions.CreateActions.action_trans_node(self.graph_view),
            image_path=Resources.BUTTON_PURPLE_40X40,
        )
        self.add_toolbar_command(
            "Outro",
            command=lambda: actions.CreateActions.action_outro_node(self.graph_view),
            image_path=Resources.BUTTON_CYAN_40X40,
        )

    def _image_section(self) -> None:
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
            "Lvls",
            command=lambda: actions.ImageActions.action_levels_node(self.graph_view),
            image_path=Resources.BUTTON_YELLOW_40X40,
        )
        self.add_toolbar_command(
            "Overlay",
            command=lambda: actions.ImageActions.action_overlay_node(self.graph_view),
            image_path=Resources.BUTTON_YELLOW_40X40,
        )
        self.add_toolbar_command(
            "Sharp",
            command=lambda: actions.ImageActions.action_sharpen_node(self.graph_view),
            image_path=Resources.BUTTON_YELLOW_40X40,
        )
        self.add_toolbar_command(
            "Thresh",
            command=lambda: actions.ImageActions.action_threshold_node(self.graph_view),
            image_path=Resources.BUTTON_YELLOW_40X40,
        )

    def _transform_section(self) -> None:
        self.add_toolbar_command(
            "Flip",
            command=lambda: actions.XformActions.action_flip_node(self.graph_view),
            image_path=Resources.BUTTON_GREEN_40X40,
        )
        self.add_toolbar_command(
            "Offset",
            command=lambda: actions.XformActions.action_offset_node(self.graph_view),
            image_path=Resources.BUTTON_GREEN_40X40,
        )
        self.add_toolbar_command(
            "Rotate",
            command=lambda: actions.XformActions.action_rotate_node(self.graph_view),
            image_path=Resources.BUTTON_GREEN_40X40,
        )

    def _math_section(self) -> None:
        self.add_toolbar_command(
            "Add",
            command=lambda: actions.MathActions.action_add_node(self.graph_view),
            image_path=Resources.BUTTON_CYAN_40X40,
        )
        self.add_toolbar_command(
            "Sub",
            command=lambda: actions.MathActions.action_subtract_node(self.graph_view),
            image_path=Resources.BUTTON_CYAN_40X40,
        )
        self.add_toolbar_command(
            "Mul",
            command=lambda: actions.MathActions.action_multiply_node(self.graph_view),
            image_path=Resources.BUTTON_CYAN_40X40,
        )
        self.add_toolbar_command(
            "Div",
            command=lambda: actions.MathActions.action_divide_node(self.graph_view),
            image_path=Resources.BUTTON_CYAN_40X40,
        )
        self.add_toolbar_command(
            "Min",
            command=lambda: actions.MathActions.action_min_node(self.graph_view),
            image_path=Resources.BUTTON_CYAN_40X40,
        )
        self.add_toolbar_command(
            "Max",
            command=lambda: actions.MathActions.action_max_node(self.graph_view),
            image_path=Resources.BUTTON_CYAN_40X40,
        )
        self.add_toolbar_command(
            "Max",
            command=lambda: actions.MathActions.action_screen_node(self.graph_view),
            image_path=Resources.BUTTON_CYAN_40X40,
        )
