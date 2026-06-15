from typing import Optional

import broker
import numpy
from PySide6TK import QtCore

from catena.core import texture
from catena.core import namespace
from catena.core.panes.pane import DockablePane
from catena.core.panes.pane import PaneConfig
from catena.core.panes.tex_viewer import image_view


class TexViewportPane(DockablePane):
    """A dockable pane that displays an image centered on a black background."""

    pane_config = PaneConfig(
        title="Texture",
        default_area=QtCore.Qt.DockWidgetArea.LeftDockWidgetArea,
    )

    def __post_init__(self) -> None:
        self._create_subscriptions()

    def create_widgets(self) -> None:
        self.image_view = image_view.ImageView(self)

    def create_layouts(self) -> None:
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.addWidget(self.image_view)

    def _create_subscriptions(self) -> None:
        broker.register_subscriber(namespace.NODE_PREVIEW, self._refresh)

    def _refresh(self, image: Optional[numpy.ndarray]) -> None:
        self.set_image(image)

    def set_image(self, image: Optional[numpy.ndarray] = None) -> None:
        """
        Display an image array, or clear the tex_viewer.

        Args:
            image (numpy.ndarray | None): Image in BGR order, as returned by
                a node's evaluate(). If None the tex_viewer is cleared.
        """
        if image is None:
            self.image_view.clear()
            return

        display = numpy.clip(image * 255.0, 0, 255).astype(numpy.uint8)
        rgb = texture.bgr_to_rgb(display)
        qimage = texture.ndarray_to_qimage(rgb)
        self.image_view.set_image(qimage)
