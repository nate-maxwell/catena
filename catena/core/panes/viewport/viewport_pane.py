from pathlib import Path

from PySide6TK import QtCore
from PySide6TK import QtGui

from catena.core.panes.pane import DockablePane
from catena.core.panes.pane import PaneConfig
from catena.core.panes.viewport import viewport_widget


class ViewportPane(DockablePane):
    """A dockable pane that displays an image centered on a black background."""

    pane_config = PaneConfig(
        title="Viewport",
        default_area=QtCore.Qt.DockWidgetArea.LeftDockWidgetArea,
    )

    def create_widgets(self) -> None:
        self.viewport_widget = viewport_widget.ViewportWidget(parent=self)

    def create_layouts(self) -> None:
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.addWidget(self.viewport_widget)

    def set_image(self, path: Path) -> None:
        """
        Load and display an image from disk.

        Args:
            path (Path): Path to the image file.
        """
        self.viewport_widget.image_view.set_image(QtGui.QImage(path.as_posix()))
