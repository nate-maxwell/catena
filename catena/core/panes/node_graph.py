from PySide6TK import QtCore

from catena.core.panes.pane import DockablePane
from catena.core.panes.pane import PaneConfig
from catena.core.nodes.graph import CatenaGraphView


class NodeGraphPane(DockablePane):
    pane_config = PaneConfig(
        title="Node Graph",
        default_area=QtCore.Qt.DockWidgetArea.BottomDockWidgetArea,
    )

    def create_widgets(self) -> None:
        self.graph_view = CatenaGraphView(self)

    def create_layouts(self) -> None:
        self.content_layout.addWidget(self.graph_view)
