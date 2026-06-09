from PySide6 import QtCore
from PySide6 import QtWidgets

from catena.core.panes.pane import DockablePane
from catena.core.panes.pane import PaneConfig


class ContentBrowser(DockablePane):
    pane_config = PaneConfig(
        title="ContentBrowser",
        default_area=QtCore.Qt.DockWidgetArea.BottomDockWidgetArea,
    )

    def create_widgets(self) -> None:
        self.label = QtWidgets.QLabel("", self.content_widget)

    def create_layouts(self) -> None:
        self.content_layout.addWidget(self.label)
        self.content_layout.addStretch()
