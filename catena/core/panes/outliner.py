from PySide6 import QtCore
from PySide6 import QtWidgets

from catena.core.panes.pane import DockablePane
from catena.core.panes.pane import PaneConfig


class OutlinerPane(DockablePane):
    pane_config = PaneConfig(
        title="Outliner",
        default_area=QtCore.Qt.DockWidgetArea.RightDockWidgetArea,
    )

    def create_widgets(self) -> None:
        self.tree = QtWidgets.QTreeWidget(self.content_widget)
        self.tree.setHeaderLabel("Scene")

    def create_layouts(self) -> None:
        self.content_layout.addWidget(self.tree)
