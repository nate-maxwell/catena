import functools

from PySide6TK import Nodes
from PySide6TK import QtCore
from PySide6TK import QtWidgets
from PySide6TK import QtWrappers
from PySide6TK import Resources

from catena.core import appdata
from catena.core import resources
from catena.core import shortcuts
from catena.core.panes.node_graph import NodeGraphPane
from catena.core.panes.properties import PropertiesPane
from catena.core.panes.resize import split_horizontal
from catena.core.panes.resize import split_vertical
from catena.core.panes.viewport import ViewportPane
from catena.core.toolbars.actions_toolbar import EditorActionToolbar
from catena.core.toolbars.client_toolbar import ClientWindowToolbar


class CatenaEditor(QtWrappers.MainWindow):
    def __init__(self) -> None:
        super().__init__(
            window_name="Catena",
            min_size=(800, 600),
            icon_path=Resources.BUTTON_BLACK_40X40,
        )

        options = QtWidgets.QMainWindow.DockOption
        self.setDockOptions(
            options.AllowNestedDocks | options.AllowTabbedDocks | options.AnimatedDocks
        )
        self.split_vertical = functools.partial(split_vertical, self)
        self.split_horizontal = functools.partial(split_horizontal, self)
        self._create_widgets()
        self._create_layouts()
        self._create_core_shortcuts()
        self._load_graph()

    def _create_widgets(self) -> None:
        self.node_graph = NodeGraphPane(self)
        self.shortcut_toolbar = ClientWindowToolbar(self)
        self.editor_toolbar = EditorActionToolbar(self, self.node_graph.graph_view)
        self.pane_properties = PropertiesPane(self)
        self.viewport = ViewportPane(self)
        self.viewport.set_image(resources.PIC_EXAMPLE_BOARD)

    def _create_layouts(self) -> None:
        self.splitDockWidget(
            self.viewport,
            self.node_graph,
            QtCore.Qt.Orientation.Horizontal,
        )
        self.splitDockWidget(
            self.pane_properties,
            self.node_graph,
            QtCore.Qt.Orientation.Vertical,
        )

        self.split_vertical(self.pane_properties, self.node_graph, 0.25)
        self.addToolBar(self.shortcut_toolbar)
        self.addToolBarBreak()
        self.addToolBar(self.editor_toolbar)

    def _load_graph(self) -> None:
        if not appdata.CATENA_GRAPH_FILE.exists():
            return

        Nodes.load(self.node_graph.graph_view, appdata.CATENA_GRAPH_FILE)

    def _create_core_shortcuts(self) -> None:
        # TODO: Find better place for this
        shortcut_manager = shortcuts.ShortcutManager(self)

        shortcut_manager.add_shortcut(
            action_name="Save",
            key_sequence="Ctrl+S",
            callback=lambda: Nodes.save(
                self.node_graph.graph_view, appdata.CATENA_GRAPH_FILE
            ),
            description="Save current project.",
            category="File",
        )
