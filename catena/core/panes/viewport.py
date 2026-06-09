from PySide6TK import QtCore
from PySide6TK import QtWidgets

from catena.core.panes.pane import DockablePane
from catena.core.panes.pane import PaneConfig


class Viewport(DockablePane):
    pane_config = PaneConfig(
        title="Viewport",
        default_area=QtCore.Qt.DockWidgetArea.LeftDockWidgetArea,
    )

    def create_widgets(self) -> None:
        self.content_widget = QtWidgets.QWidget()

    def create_layouts(self) -> None:
        self.content_layout.addWidget(self.content_widget)

    @staticmethod
    def _tick(surface, _) -> None:
        surface.fill("black")
