from typing import Optional

import numpy
from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets
from PySide6TK.Nodes import PortType

from catena import texture
from catena.nodes.base import CatenaNode
from catena.nodes.generate import IMAGE_NODE_COLOR


class GeneratorNode(CatenaNode):
    """A node with an output port and a live preview of its generated image."""

    _COLOR_HEADER = IMAGE_NODE_COLOR
    _PREVIEW_SIZE: int = 96
    _PREVIEW_MARGIN: int = 8

    def __init__(self, title: str, width: int = 160) -> None:
        port_area_height = self._PORT_MARGIN * 2
        body_height = port_area_height + self._PREVIEW_SIZE + self._PREVIEW_MARGIN * 2
        super().__init__(title, width, body_height)
        self._preview_pixmap: Optional[QtGui.QPixmap] = None
        self.evaluate()

    def _build(self) -> None:
        self.port_out = self.add_port(PortType.OUTPUT, "Output")

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        result = inputs.get("Input")
        self._update_preview(result)
        return result

    def evaluate(self) -> Optional[numpy.ndarray]:
        image = super().evaluate()
        self._update_preview(image)
        return image

    def _update_preview(self, image: Optional[numpy.ndarray]) -> None:
        """
        Update the cached preview pixmap from the given image.

        Args:
            image (numpy.ndarray | None): The image to preview, in float32
                BGR format with values in [0, 1], or None to clear.
        """
        if image is None:
            self._preview_pixmap = None
            self.update()
            return

        display = numpy.clip(image * 255.0, 0, 255).astype(numpy.uint8)
        rgb = texture.bgr_to_rgb(display)
        qimage = texture.ndarray_to_qimage(rgb)
        pixmap = QtGui.QPixmap.fromImage(qimage)
        self._preview_pixmap = pixmap.scaled(
            self._PREVIEW_SIZE,
            self._PREVIEW_SIZE,
            QtCore.Qt.AspectRatioMode.KeepAspectRatio,
            QtCore.Qt.TransformationMode.SmoothTransformation,
        )
        self.update()

    def paint(
        self,
        painter: QtGui.QPainter,
        option: QtWidgets.QStyleOptionGraphicsItem,
        widget: Optional[QtWidgets.QWidget] = None,
    ) -> None:
        """
        Paint the node, then draw the preview image below the ports.

        Args:
            painter (QtGui.QPainter): The painter.
            option (QtWidgets.QStyleOptionGraphicsItem): Style options.
            widget (QtWidgets.QWidget | None): Optional widget.
        """
        super().paint(painter, option, widget)

        if self._preview_pixmap is None:
            return

        preview_y = (
            self._HEADER_HEIGHT
            + self.body_height
            - self._PREVIEW_SIZE
            - self._PREVIEW_MARGIN
        )
        preview_x = (self.width - self._preview_pixmap.width()) / 2.0

        painter.drawPixmap(int(preview_x), int(preview_y), self._preview_pixmap)
