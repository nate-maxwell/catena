from pathlib import Path

import broker
from PySide6TK import QtCore

from catena.core import namespace
from catena.core.nodes.base import CatenaNode
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
        broker.register_subscriber(namespace.NODE_DOUBLE_CLICK, self._refresh)

    def _refresh(self, node: CatenaNode) -> None:
        if not node.contains_field("filepath"):
            # Likely not a node that contains an image to display
            return

        image_str = node.get_field_value("filepath")
        if not image_str:
            self.set_image()
            return

        image_path = Path(image_str)
        if not image_path.exists():
            self.set_image()
            return

        self.set_image(image_path)

    def set_image(self, path: Path | None = None) -> None:
        """
        Load and display an image from disk.

        Args:
            path (Path | None): Path to the image file. If path does not exist
                or is set to None the image is cleared. Defaults to None.
        """
        if path is None or not path.exists():
            self.viewport_widget.image_view.clear()
            return

        self.viewport_widget.image_view.set_image_from_path(path)
