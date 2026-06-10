from PySide6TK import QtCore

from catena.core import example_graph
from catena.core.panes.pane import DockablePane
from catena.core.panes.pane import PaneConfig


class NodeGraphPane(DockablePane):
    pane_config = PaneConfig(
        title="Node Graph",
        default_area=QtCore.Qt.DockWidgetArea.BottomDockWidgetArea,
    )

    def create_widgets(self) -> None:
        self.graph = example_graph.NodeGraphWindow()

    def create_layouts(self) -> None:
        self.content_layout.addWidget(self.graph)
