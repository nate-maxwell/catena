from PySide6TK import QtWidgets
from PySide6TK import QtWrappers
from PySide6TK import Resources

from catena.core.nodes.graph import CatenaGraphView
from catena.core.toolbars import actions


class MathToolbar(QtWrappers.Toolbar):

    def __init__(self, parent: QtWidgets.QWidget, graph_view: CatenaGraphView) -> None:
        super().__init__(
            "Math Toolbar", default_button_resolution=[40, 40], parent=parent
        )
        self.graph_view = graph_view

    def build(self) -> None:
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
            "Screen",
            command=lambda: actions.MathActions.action_screen_node(self.graph_view),
            image_path=Resources.BUTTON_CYAN_40X40,
        )
        self.add_toolbar_command(
            "Sin",
            command=lambda: actions.MathActions.action_sin_node(self.graph_view),
            image_path=Resources.BUTTON_CYAN_40X40,
        )
