from typing import Optional

import broker
import numpy
from PySide6TK import QtCore

from catena.core import namespace
from catena.core import texture
from catena.core.panes.obj_viewer import obj_viewer
from catena.core.panes.pane import DockablePane
from catena.core.panes.pane import PaneConfig


class ObjViewportPane(DockablePane):
    """A dockable pane that displays an object with textures."""

    pane_config = PaneConfig(
        title="Model",
        default_area=QtCore.Qt.DockWidgetArea.LeftDockWidgetArea,
    )

    def __post_init__(self) -> None:
        self._create_subscriptions()

    def create_widgets(self) -> None:
        self.obj_view = obj_viewer.ObjViewer(parent=self)

    def create_layouts(self) -> None:
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.addWidget(self.obj_view)

    def _create_subscriptions(self) -> None:
        broker.register_subscriber(namespace.MODEL_UPDATED_TEXTURE, self._refresh)

    def _refresh(
        self, image: Optional[numpy.ndarray], texture_type: texture.TextureType
    ) -> None:

        match texture_type:
            case texture.TextureType.ALBEDO:
                self.obj_view.set_albedo_texture(image)
            case texture.TextureType.ROUGHNESS:
                self.obj_view.set_roughness_texture(image)
            case texture.TextureType.METALLIC:
                self.obj_view.set_metallic_texture(image)
            case texture.TextureType.AO:
                self.obj_view.set_ao_texture(image)
            case texture.TextureType.HEIGHT:
                self.obj_view.set_height_texture(image)
            case texture.TextureType.NORMAL:
                self.obj_view.set_normal_texture(image)
