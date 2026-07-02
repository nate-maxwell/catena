import logging
from typing import Optional

import broker
import numpy
from PySide6TK import QtCore

from catena import namespace
from catena import texture
from catena.preferences import preferences
from catena.panes.obj_viewer import obj_widget
from catena.panes.pane import DockablePane
from catena.panes.pane import PaneConfig

logger = logging.getLogger(__name__)


class ObjViewportPane(DockablePane):
    """A dockable pane that displays an object with textures."""

    pane_config = PaneConfig(
        title="Model",
        default_area=QtCore.Qt.DockWidgetArea.LeftDockWidgetArea,
    )

    def __post_init__(self) -> None:
        self._create_subscriptions()
        logger.info("Object view pane initialized")

    def create_widgets(self) -> None:
        self.obj_wid = obj_widget.ObjectViewerWidget(self)

    def create_layouts(self) -> None:
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.addWidget(self.obj_wid)

    def _create_subscriptions(self) -> None:
        broker.register_subscriber(namespace.MODEL_UPDATED_TEXTURE, self._refresh)
        broker.register_subscriber(
            namespace.PREFERENCES_UPDATED, self._on_preferences_updated
        )

    def _on_preferences_updated(self) -> None:
        topic_prefs = preferences.Preferences()["general_preferences"]
        self.obj_wid.obj_view.set_displacement_scale(topic_prefs.displacement_scale)

    def _refresh(
        self, image: Optional[numpy.ndarray], texture_type: texture.TextureType
    ) -> None:

        match texture_type:
            case texture.TextureType.ALBEDO:
                self.obj_wid.obj_view.set_albedo_texture(image)
            case texture.TextureType.ROUGHNESS:
                self.obj_wid.obj_view.set_roughness_texture(image)
            case texture.TextureType.METALLIC:
                self.obj_wid.obj_view.set_metallic_texture(image)
            case texture.TextureType.AO:
                self.obj_wid.obj_view.set_ao_texture(image)
            case texture.TextureType.HEIGHT:
                self.obj_wid.obj_view.set_height_texture(image)
            case texture.TextureType.NORMAL:
                self.obj_wid.obj_view.set_normal_texture(image)
