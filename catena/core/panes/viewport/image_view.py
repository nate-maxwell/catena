from pathlib import Path

from PySide6TK import QtCore
from PySide6TK import QtGui
from PySide6TK import QtWidgets


class ImageView(QtWidgets.QWidget):
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

    def set_image_from_path(self, path: Path) -> None:
        """
        Load and display an image from disk.

        Args:
            path (Path): Path to the image file.
        """
        self.set_image(QtGui.QImage(path.as_posix()))

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

    def clear(self) -> None:
        """Clear the displayed image and trigger a repaint."""
        self.image = None
        self.update()
