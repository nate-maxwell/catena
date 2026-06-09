from dataclasses import dataclass
from dataclasses import field

from PySide6TK import QtCore
from PySide6TK import QtWidgets


@dataclass
class PaneConfig(object):
    """
    Configuration for a DockablePane's placement and behavior.

    Args:
        title (str): The title shown in the pane's title bar.
        default_area (QtCore.Qt.DockWidgetArea): The dock area to attach to on first show.
        allowed_areas (QtCore.Qt.DockWidgetArea): Bitwise OR of areas the pane may be docked into.
        features (QtWidgets.QDockWidget.DockWidgetFeature): Dock widget feature flags.
        starts_floating (bool): Whether the pane opens as a floating window instead of docked.
        min_size (tuple[int, int]): Minimum (width, height) in pixels.
    """

    title: str = "Pane"
    default_area: QtCore.Qt.DockWidgetArea = QtCore.Qt.DockWidgetArea.LeftDockWidgetArea
    allowed_areas: QtCore.Qt.DockWidgetArea = (
        QtCore.Qt.DockWidgetArea.LeftDockWidgetArea
        | QtCore.Qt.DockWidgetArea.RightDockWidgetArea
        | QtCore.Qt.DockWidgetArea.TopDockWidgetArea
        | QtCore.Qt.DockWidgetArea.BottomDockWidgetArea
    )
    features: QtWidgets.QDockWidget.DockWidgetFeature = (
        QtWidgets.QDockWidget.DockWidgetFeature.DockWidgetMovable
        | QtWidgets.QDockWidget.DockWidgetFeature.DockWidgetFloatable
        | QtWidgets.QDockWidget.DockWidgetFeature.DockWidgetClosable
    )
    starts_floating: bool = False
    min_size: tuple[int, int] = field(default_factory=lambda: (200, 150))


class DockablePane(QtWidgets.QDockWidget):
    """
    Base class for dockable catena panes.

    Subclass this and implement ``create_widgets``, ``create_layouts``,
    and ``create_connections`` to build the pane's content. All child
    widgets should be parented to ``self.content_widget``.

    Args:
        main_window (QtWidgets.QMainWindow): The main window to dock into.
        config (PaneConfig): Placement and behavior configuration.

    Example:

        class OutlinerPane(DockablePane):
            pane_config = PaneConfig(
                title="Outliner",
                default_area=QtCore.Qt.DockWidgetArea.RightDockWidgetArea,
            )

            def create_widgets(self) -> None:
                self.tree = QtWidgets.QTreeWidget(self.content_widget)
                self.tree.setHeaderLabel("Scene")

            def create_layouts(self) -> None:
                self.content_layout.addWidget(self.tree)
    """

    pane_config: PaneConfig = PaneConfig()

    def __init__(
        self,
        main_window: QtWidgets.QMainWindow,
        config: PaneConfig | None = None,
    ) -> None:
        self._config = config or self.__class__.pane_config
        super().__init__(self._config.title, main_window)

        self.setAllowedAreas(self._config.allowed_areas)
        self.setFeatures(self._config.features)

        self.content_widget = QtWidgets.QWidget()
        self.content_layout = QtWidgets.QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(4, 4, 4, 4)
        self.content_layout.setSpacing(4)
        self.setWidget(self.content_widget)
        self.content_widget.setMinimumSize(0, 0)

        self.create_widgets()
        self.create_layouts()
        self.create_connections()

        main_window.addDockWidget(self._config.default_area, self)

        if self._config.starts_floating:
            self.setFloating(True)

    def minimumSizeHint(self) -> QtCore.QSize:
        return QtCore.QSize(0, 0)

    # -----Subclass interface--------------------------------------------------

    def create_widgets(self) -> None:
        """Create and parent child widgets to ``self.content_widget``."""

    def create_layouts(self) -> None:
        """Add widgets to ``self.content_layout`` or set custom layouts."""

    def create_connections(self) -> None:
        """Connect signals and slots."""

    # -----Convenience---------------------------------------------------------

    def toggle_visibility(self) -> None:
        """Toggle the pane between visible and hidden."""
        self.setVisible(not self.isVisible())

    def raise_pane(self) -> None:
        """Bring the pane to front when tabbed with other panes."""
        self.show()
        self.raise_()
