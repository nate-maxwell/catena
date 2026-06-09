import functools

from PySide6TK import QtCore
from PySide6TK import QtWidgets
from PySide6TK import QtWrappers

import catena.core.toolbar
from catena.core.panes.node_graph import NodeGraphPane
from catena.core.panes.outliner import OutlinerPane
from catena.core.panes.properties import PropertiesPane
from catena.core.panes.resize import split_horizontal
from catena.core.panes.resize import split_vertical
from catena.core.panes.viewport import Viewport


class CatenaEditor(QtWrappers.MainWindow):
    def __init__(self) -> None:
        super().__init__(
            window_name="Catena",
            min_size=(800, 600),
            icon_path=QtWrappers.BUTTON_BLACK_40X40,
        )

        options = QtWidgets.QMainWindow.DockOption
        self.setDockOptions(options.AllowNestedDocks | options.AllowTabbedDocks | options.AnimatedDocks)
        self.split_vertical = functools.partial(split_vertical, self)
        self.split_horizontal = functools.partial(split_horizontal, self)
        self._create_widgets()
        self._create_layouts()
        self._create_connections()

    def _create_widgets(self) -> None:
        self.shortcut_toolbar = catena.core.toolbar.ClientWindowToolbar(self)
        self.editor_toolbar = catena.core.toolbar.EditorActionToolbar()
        self.pane_outliner = OutlinerPane(self)
        self.pane_properties = PropertiesPane(self)
        self.node_graph = NodeGraphPane(self)
        self.viewport = Viewport(self)

    def _create_layouts(self) -> None:
        self.splitDockWidget(
            self.viewport,
            self.pane_outliner,
            QtCore.Qt.Orientation.Horizontal,
        )
        self.splitDockWidget(
            self.pane_outliner,
            self.pane_properties,
            QtCore.Qt.Orientation.Vertical,
        )
        self.splitDockWidget(
            self.viewport,
            self.node_graph,
            QtCore.Qt.Orientation.Vertical,
        )

        self.split_vertical(self.pane_outliner, self.pane_properties, 0.5)
        self.split_vertical(self.viewport, self.node_graph, 0.6)
        self.split_horizontal(self.viewport, self.pane_outliner, 0.75)
        self.addToolBar(self.shortcut_toolbar)
        self.addToolBarBreak()
        self.addToolBar(self.editor_toolbar)

    def _create_connections(self) -> None:
        pass
