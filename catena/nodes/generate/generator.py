from typing import Optional

import broker
import numpy
from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets
from PySide6TK.Nodes import PortType

from catena import namespace
from catena import texture
from catena.nodes.node_gui import CatenaNode
from catena.nodes.generate import IMAGE_NODE_COLOR
from catena.preferences import preferences


class GeneratorNode(CatenaNode):
    """A node with an output port and a live preview of its generated image."""

    _COLOR_HEADER = IMAGE_NODE_COLOR
    _PREVIEW_SIZE: int = 96
    _PREVIEW_MARGIN: int = 8
    _WIDTH: int = 1024
    _HEIGHT: int = _WIDTH

    def __init__(self, title: str, width: int = 160) -> None:
        port_area_height = self._PORT_MARGIN * 2
        body_height = port_area_height + self._PREVIEW_SIZE + self._PREVIEW_MARGIN * 2
        super().__init__(title, width, body_height)
        self._preview_pixmap: Optional[QtGui.QPixmap] = None
        self._create_subscriptions()
        self._evaluate_resolution()

    def _create_subscriptions(self) -> None:
        broker.register_subscriber(
            namespace.PREFERENCES_UPDATED, self._evaluate_resolution
        )

    def _build(self) -> None:
        self.port_out = self.add_port(PortType.OUTPUT, "Output")

    def _evaluate_resolution(self) -> None:
        self._invalidate_downstream()
        self._refresh_downstream_write_nodes()

        topic_prefs = preferences.Preferences().general_preferences
        GeneratorNode._WIDTH = topic_prefs.texture_resolution
        GeneratorNode._HEIGHT = GeneratorNode._WIDTH

        # Easiest way to invalidate cache and update preview
        self._on_field_changed(self)

    def _on_field_changed(self, node: "CatenaNode") -> None:
        super()._on_field_changed(node)
        image = self.evaluate()
        self._update_preview(image)

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

    def itemChange(
        self, change: QtWidgets.QGraphicsItem.GraphicsItemChange, value: object
    ) -> object:
        if change == QtWidgets.QGraphicsItem.GraphicsItemChange.ItemSceneHasChanged:
            if self.scene() is not None:
                self.evaluate()
        return super().itemChange(change, value)

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
