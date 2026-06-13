import functools

from PySide6TK import QtCore
from PySide6TK import QtGui
from PySide6TK import QtWidgets
from PySide6TK import QtWrappers

from catena.core import resources
from catena.core import shortcuts
from catena.core.prefs import preferences
from catena.core.panes.node_graph import NodeGraphPane
from catena.core.panes.properties import PropertiesPane
from catena.core.panes.resize import split_horizontal
from catena.core.panes.resize import split_vertical
from catena.core.panes.viewport.viewport_pane import ViewportPane
from catena.core.toolbars.actions_toolbar import EditorActionToolbar
from catena.core.toolbars.client_toolbar import ClientWindowToolbar
from catena.core.toolbars.status_bar import StatusBar

WINDOW_STATE_VERSION = 1
"""
A version number representing the initial pane structure.
This should be incremented whenever a new pane is added to the default layout.
"""

win_state = "window_state"
win_geo = "window_geometry"
org = "NateMaxwell"
app = "Catena"


class CatenaEditor(QtWrappers.MainWindow):
    def __init__(self) -> None:
        super().__init__(
            window_name="Catena",
            min_size=(800, 600),
            icon_path=resources.ICON_CATENA,
        )
        preferences.initialize()
        shortcuts.ShortcutManager(self)

        options = QtWidgets.QMainWindow.DockOption
        self.setDockOptions(
            options.AllowNestedDocks | options.AllowTabbedDocks | options.AnimatedDocks
        )
        self.split_vertical = functools.partial(split_vertical, self)
        self.split_horizontal = functools.partial(split_horizontal, self)
        self._create_widgets()
        self._create_layouts()
        self._initialize_shortcut_manager()
        self._restore_window_state()
        self.pane_graph.load_graph()

    def _create_widgets(self) -> None:
        self.pane_graph = NodeGraphPane(self)
        self.pane_properties = PropertiesPane(self)
        self.pane_viewport = ViewportPane(self)

        self.shortcut_toolbar = ClientWindowToolbar(self)
        self.editor_toolbar = EditorActionToolbar(self, self.pane_graph.graph_view)
        self.status_bar = StatusBar(self)

    def _create_layouts(self) -> None:
        self.splitDockWidget(
            self.pane_viewport,
            self.pane_graph,
            QtCore.Qt.Orientation.Horizontal,
        )
        self.splitDockWidget(
            self.pane_properties,
            self.pane_graph,
            QtCore.Qt.Orientation.Vertical,
        )

        self.split_vertical(self.pane_properties, self.pane_graph, 0.25)
        self.addToolBar(self.shortcut_toolbar)
        self.addToolBarBreak()
        self.addToolBar(self.editor_toolbar)
        self.addToolBar(QtCore.Qt.ToolBarArea.BottomToolBarArea, self.status_bar)

    def _initialize_shortcut_manager(self) -> None:
        shortcuts.ShortcutManager(self)

    def _restore_window_state(self) -> None:
        settings = QtCore.QSettings(org, app)
        state = settings.value(win_state)

        if state is not None:
            self.restoreState(state, WINDOW_STATE_VERSION)

        geometry = settings.value(win_geo)
        if geometry is not None:
            self.restoreGeometry(geometry)

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        settings = QtCore.QSettings(org, app)
        state = self.saveState(WINDOW_STATE_VERSION)
        geo = self.saveGeometry()
        settings.setValue(win_state, state)
        settings.setValue(win_geo, geo)
        settings.sync()
