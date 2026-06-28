import logging

from PySide6 import QtCore
from catena import api

import stats_widget

logger = logging.getLogger(__name__)


class GraphStatsPane(api.DockablePane):
    pane_config = api.PaneConfig(
        title="GraphStats",
        default_area=QtCore.Qt.DockWidgetArea.RightDockWidgetArea,
    )

    def __post_init__(self) -> None:
        logger.info("Graph Stats viewer pane initialized")

    def create_widgets(self) -> None:
        self.stats_widget = stats_widget.GraphStatsWidget(self)

    def create_layouts(self) -> None:
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.addWidget(self.stats_widget)
