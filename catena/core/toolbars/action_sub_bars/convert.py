from PySide6TK import QtWidgets
from PySide6TK import QtWrappers
from PySide6TK import Resources

from catena.core.nodes.graph import CatenaGraphView
from catena.core.toolbars import actions


class ConvertToolbar(QtWrappers.Toolbar):

    def __init__(self, parent: QtWidgets.QWidget, graph_view: CatenaGraphView) -> None:
        super().__init__(
            "Convert Toolbar", default_button_resolution=[40, 40], parent=parent
        )
        self.graph_view = graph_view

    def build(self) -> None:
        self.add_toolbar_command(
            "H2AO",
            command=lambda: actions.ConvertActions.action_h2ao_node(self.graph_view),
            image_path=Resources.BUTTON_BLUE_40X40,
        )
        self.add_toolbar_command(
            "H2N",
            command=lambda: actions.ConvertActions.action_h2m_node(self.graph_view),
            image_path=Resources.BUTTON_BLUE_40X40,
        )
