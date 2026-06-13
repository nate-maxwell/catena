from typing import Optional

import broker
import numpy
from PySide6 import QtGui
from PySide6TK import QtCore

from catena.core import namespace
from catena.core import color
from catena.core.panes.pane import DockablePane
from catena.core.panes.pane import PaneConfig
from catena.core.panes.viewport import viewport_widget


class ViewportPane(DockablePane):
    """A dockable pane that displays an image centered on a black background."""

    pane_config = PaneConfig(
        title="Viewport",
        default_area=QtCore.Qt.DockWidgetArea.LeftDockWidgetArea,
    )

    def __post_init__(self) -> None:
        self._create_subscriptions()

    def create_widgets(self) -> None:
        self.viewport_widget = viewport_widget.ViewportWidget(parent=self)

    def create_layouts(self) -> None:
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.addWidget(self.viewport_widget)

    def _create_subscriptions(self) -> None:
        broker.register_subscriber(namespace.NODE_PREVIEW, self._refresh)

    def _refresh(self, image: Optional[numpy.ndarray]) -> None:
        self.set_image(image)

    def set_image(self, image: Optional[numpy.ndarray] = None) -> None:
        """
        Display an image array, or clear the viewport.

        Args:
            image (numpy.ndarray | None): Image in BGR order, as returned by
                a node's evaluate(). If None the viewport is cleared.
        """
        if image is None:
            self.viewport_widget.image_view.clear()
            return

        rgb = color.bgr_to_rgb(image)
        qimage = color.ndarray_to_qimage(rgb)
        self.viewport_widget.image_view.set_image(qimage)
