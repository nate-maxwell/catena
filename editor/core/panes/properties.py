from PySide6 import QtCore
from PySide6 import QtWidgets

from editor.core.panes.pane import DockablePane
from editor.core.panes.pane import PaneConfig


class PropertiesPane(DockablePane):
    pane_config = PaneConfig(
        title="Properties",
        default_area=QtCore.Qt.DockWidgetArea.RightDockWidgetArea,
    )

    def create_widgets(self) -> None:
        self.label = QtWidgets.QLabel("", self.content_widget)

    def create_layouts(self) -> None:
        self.content_layout.addWidget(self.label)
        self.content_layout.addStretch()
