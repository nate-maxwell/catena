import functools
import logging

from PySide6TK import QtCore
from PySide6TK import QtGui
from PySide6TK import QtWidgets
from PySide6TK import QtWrappers

import catena.plugins.loader
from catena.api import graph_api
from catena.api import toolbar_api
from catena import resources
from catena import session
from catena import shortcuts
from catena.panes.node_graph.node_graph import NodeGraphPane
from catena.panes.obj_viewer.obj_viewport_pane import ObjViewportPane
from catena.panes.properties import PropertiesPane
from catena.panes.resize import split_horizontal
from catena.panes.resize import split_vertical
from catena.panes.tex_viewer.tex_viewport_pane import TexViewportPane
from catena.plugins import plugin_record
from catena.preferences import preferences
from catena.toolbars.shelf_toolbar.actions_toolbar import EditorActionToolbar
from catena.toolbars.menu_toolbar import MenuToolbar
from catena.toolbars.status_bar import StatusBar

logger = logging.getLogger(__name__)

WINDOW_STATE_VERSION = 10
"""
A version number representing the initial pane structure.
This should be incremented whenever a new pane is added to the default layout.
"""

win_state = "window_state"
win_geo = "window_geometry"
org = "NateMaxwell"
app = "Catena"


# settings = QtCore.QSettings(org, app)
# settings.clear()


class CatenaEditor(QtWrappers.MainWindow):
    def __init__(self) -> None:
        super().__init__(
            window_name="Catena",
            min_size=(800, 600),
            icon_path=resources.ICON_CATENA,
        )
        self._initialize_singleton_subsystems()

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
        QtCore.QTimer.singleShot(0, self.pane_node_graph.load_previous_graph)
        logger.info("-" * 30)

        # Although not strictly necessary, plugin loading should happen after
        # everything else is initialized so that any references to existing
        # systems or widgets is valid.
        catena.plugins.loader.load_plugins()

    def _initialize_singleton_subsystems(self) -> None:
        """Ensures all the singleton classes for "global" data are loaded."""
        preferences.initialize()
        plugin_record.initialize()
        session.initialize()
        shortcuts.ShortcutManager(self)

    def _create_widgets(self) -> None:
        self.pane_object_viewport = ObjViewportPane(self)
        self.pane_texture_viewport = TexViewportPane(self)
        self.pane_node_graph = NodeGraphPane(self)
        graph_api.init_graph_pane(self.pane_node_graph)
        self.pane_properties = PropertiesPane(self)

        self.menu_toolbar = MenuToolbar(self)
        toolbar_api.init_menu_toolbar_ref(self.menu_toolbar)
        self.editor_toolbar = EditorActionToolbar(self)
        toolbar_api.init_actions_toolbar_ref(self.editor_toolbar)
        self.status_bar = StatusBar(self)

    def _create_layouts(self) -> None:
        self.splitDockWidget(
            self.pane_object_viewport,
            self.pane_node_graph,
            QtCore.Qt.Orientation.Horizontal,
        )
        self.splitDockWidget(
            self.pane_object_viewport,
            self.pane_texture_viewport,
            QtCore.Qt.Orientation.Vertical,
        )
        self.splitDockWidget(
            self.pane_node_graph,
            self.pane_properties,
            QtCore.Qt.Orientation.Horizontal,
        )

        self.split_horizontal(self.pane_node_graph, self.pane_properties, 0.7)
        self.split_horizontal(self.pane_object_viewport, self.pane_node_graph, 0.3)
        self.split_vertical(self.pane_object_viewport, self.pane_texture_viewport, 0.5)

        self.addToolBar(QtCore.Qt.ToolBarArea.TopToolBarArea, self.menu_toolbar)
        self.addToolBar(QtCore.Qt.ToolBarArea.TopToolBarArea, self.editor_toolbar)
        self.insertToolBarBreak(self.editor_toolbar)
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
