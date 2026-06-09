from pathlib import Path

from PySide6TK import QtCore
from PySide6TK import QtGui
from PySide6TK import QtWidgets

from catena.core.panes.pane import DockablePane
from catena.core.panes.pane import PaneConfig


class _ImageView(QtWidgets.QWidget):
    """
    A widget that draws an image centered on a black background.

    Args:
        parent (QtWidgets.QWidget | None): Optional parent widget.
    Attributes:
        image (QtGui.QImage | None): The currently displayed image.
    """

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.image: QtGui.QImage | None = None
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Expanding,
        )
        self.setMinimumSize(0, 0)

    def set_image(self, image: QtGui.QImage) -> None:
        """
        Set the image to display and trigger a repaint.

        Args:
            image (QtGui.QImage): The image to display.
        """
        self.image = image
        self.update()

    def sizeHint(self) -> QtCore.QSize:
        return QtCore.QSize(0, 0)

    def minimumSizeHint(self) -> QtCore.QSize:
        return QtCore.QSize(0, 0)

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        painter = QtGui.QPainter(self)
        painter.fillRect(self.rect(), QtCore.Qt.GlobalColor.black)

        if self.image is not None and not self.image.isNull():
            scaled = self.image.scaled(
                self.size(),
                QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                QtCore.Qt.TransformationMode.SmoothTransformation,
            )
            x = (self.width() - scaled.width()) // 2
            y = (self.height() - scaled.height()) // 2
            painter.drawImage(x, y, scaled)

        painter.end()


class Viewport(DockablePane):
    """A dockable pane that displays an image centered on a black background."""

    pane_config = PaneConfig(
        title="Viewport",
        default_area=QtCore.Qt.DockWidgetArea.LeftDockWidgetArea,
    )

    def create_widgets(self) -> None:
        self.image_view = _ImageView(self.content_widget)

    def create_layouts(self) -> None:
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.addWidget(self.image_view)

    def set_image(self, path: Path) -> None:
        """
        Load and display an image from disk.

        Args:
            path (Path): Path to the image file.
        """
        self.image_view.set_image(QtGui.QImage(path.as_posix()))
