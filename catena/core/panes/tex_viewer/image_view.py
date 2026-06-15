from pathlib import Path

from PySide6TK import QtCore
from PySide6TK import QtGui
from PySide6TK import QtWidgets

from catena.core import shortcuts


class ImageView(QtWidgets.QWidget):
    """
    A widget that draws an image centered on a black background.

    Supports mouse wheel zoom and middle-mouse-button drag to pan.

    Args:
        parent (QtWidgets.QWidget | None): Optional parent widget.
    Attributes:
        image (QtGui.QImage | None): The currently displayed image.
    """

    _ZOOM_MIN: float = 0.1
    _ZOOM_MAX: float = 20.0
    _ZOOM_STEP: float = 0.15

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.image: QtGui.QImage | None = None
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Expanding,
        )
        self.setMinimumSize(0, 0)
        self.setContentsMargins(0, 0, 0, 0)

        self._zoom: float = 1.0
        self._pan_offset: QtCore.QPointF = QtCore.QPointF(0.0, 0.0)
        self._pan_active: bool = False
        self._pan_origin: QtCore.QPoint = QtCore.QPoint()

        self._create_shortcuts()

    def _create_shortcuts(self) -> None:
        # Shortcut Manager
        scm = shortcuts.ShortcutManager()

        scm.add_shortcut(
            action_name="CenterViewport",
            key_sequence=QtGui.QKeySequence("F").toString(),
            callback=self.recenter,
            description="Recenter the texture viewport.",
            category="Viewport",
        )

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

    def reset_view(self) -> None:
        """Reset zoom and pan to their default values and trigger a repaint."""
        self._zoom = 1.0
        self._pan_offset = QtCore.QPointF(0.0, 0.0)
        self.update()

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        painter = QtGui.QPainter(self)
        painter.fillRect(self.rect(), QtCore.Qt.GlobalColor.black)

        if self.image is not None and not self.image.isNull():
            base_scaled = self.image.scaled(
                self.size(),
                QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                QtCore.Qt.TransformationMode.SmoothTransformation,
            )
            x = (self.width() - base_scaled.width()) // 2
            y = (self.height() - base_scaled.height()) // 2

            painter.translate(self.rect().center())
            painter.scale(self._zoom, self._zoom)
            painter.translate(-self.rect().center())
            painter.translate(self._pan_offset)

            painter.drawImage(x, y, base_scaled)

        painter.end()

    def clear(self) -> None:
        """Clear the displayed image and trigger a repaint."""
        self.image = None
        self.update()

    def wheelEvent(self, event: QtGui.QWheelEvent) -> None:
        delta = event.angleDelta().y()
        factor = 1.0 + self._ZOOM_STEP if delta > 0 else 1.0 - self._ZOOM_STEP
        new_zoom = self._zoom * factor
        if self._ZOOM_MIN <= new_zoom <= self._ZOOM_MAX:
            self._zoom = new_zoom
            self.update()

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        if event.button() == QtCore.Qt.MouseButton.MiddleButton:
            self._pan_active = True
            self._pan_origin = event.position().toPoint()
            self.setCursor(QtCore.Qt.CursorShape.ClosedHandCursor)
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        if self._pan_active:
            current_pos = event.position().toPoint()
            delta = current_pos - self._pan_origin
            self._pan_origin = current_pos
            self._pan_offset += QtCore.QPointF(
                delta.x() / self._zoom, delta.y() / self._zoom
            )
            self.update()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        if event.button() == QtCore.Qt.MouseButton.MiddleButton:
            self._pan_active = False
            self.setCursor(QtCore.Qt.CursorShape.ArrowCursor)
            return
        super().mouseReleaseEvent(event)

    def recenter(self) -> None:
        """
        Reset pan offset to center the image without changing zoom, and trigger
        a repaint.
        """
        self._pan_offset = QtCore.QPointF(0.0, 0.0)
        self.update()
