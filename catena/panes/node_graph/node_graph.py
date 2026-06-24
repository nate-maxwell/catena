import logging
from pathlib import Path
from typing import Optional

import broker
from PySide6TK import Nodes
from PySide6TK import QtCore
from PySide6TK import QtGui
from PySide6TK import QtWidgets

from catena import appdata
from catena import file
from catena import namespace
from catena import session
from catena import shortcuts
from catena.nodes.file.write import WriteNode
from catena.nodes.graph_gui import GuiGraphView
from catena.panes.pane import DockablePane
from catena.panes.pane import PaneConfig
from catena.preferences.preferences import Preferences
from catena.preferences import category_data
from catena.panes.node_graph import serialize

logger = logging.getLogger(__name__)

UNSAVED = f"Unsaved{appdata.CATENA_FILE_SUFFIX}"


class GraphTab(object):
    """Holds the state for a single graph tab."""

    def __init__(self, graph_view: GuiGraphView, file_path: Path) -> None:
        self.graph_view = graph_view
        self.file_path = file_path


class NodeGraphPane(DockablePane):
    pane_config = PaneConfig(
        title="Node Graph",
        default_area=QtCore.Qt.DockWidgetArea.BottomDockWidgetArea,
    )

    def __post_init__(self) -> None:
        self._create_shortcuts()
        self._create_subscriptions()
        self._on_preferences_updated()
        logger.info("Graph pane initialized")

    def create_widgets(self) -> None:
        self._tabs: dict[int, GraphTab] = {}
        self.tab_widget = QtWidgets.QTabWidget(self)
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.setMovable(True)
        self.tab_widget.tabCloseRequested.connect(self._on_tab_close_requested)
        self.tab_widget.currentChanged.connect(self._on_tab_changed)
        self._open_new_tab(Path.home() / UNSAVED)

    def create_layouts(self) -> None:
        self.content_layout.addWidget(self.tab_widget)

    @property
    def graph_view(self) -> GuiGraphView:
        """Return the currently active graph view."""
        return self._current_tab().graph_view

    def _current_tab(self) -> GraphTab:
        """Return the currently active tab."""
        return self._tabs[self.tab_widget.currentIndex()]

    def _open_new_tab(self, file_path: Path) -> GuiGraphView:
        """
        Open a new graph tab with a fresh GuiGraphView.

        Args:
            file_path (Path): The file path associated with this tab.
        Returns:
            GuiGraphView: The newly created graph view.
        """
        view = GuiGraphView(self)
        index = self.tab_widget.addTab(view, file_path.stem)
        self._tabs[index] = GraphTab(view, file_path)
        self.tab_widget.setCurrentIndex(index)
        self._apply_preferences_to_view(view)
        return view

    def _on_tab_close_requested(self, index: int) -> None:
        if self.tab_widget.count() <= 1:
            return
        self.tab_widget.removeTab(index)
        self._tabs.pop(index, None)
        self._rebuild_tab_index()

    def _on_tab_changed(self, index: int) -> None:
        tab = self._tabs.get(index)
        if tab is None:
            return
        broker.emit(namespace.FILE_CHANGED, file_path=tab.file_path)

    def _rebuild_tab_index(self) -> None:
        """Rebuild the tab index map after a tab is removed."""
        old_tabs = list(self._tabs.values())
        self._tabs.clear()
        for i in range(self.tab_widget.count()):
            if i < len(old_tabs):
                self._tabs[i] = old_tabs[i]

    def open_subgraph(self, file_path: Path) -> None:
        """
        Open a subgraph file in a new tab, or switch to it if already open.

        Args:
            file_path (Path): The subgraph file path to open.
        """
        for index, tab in self._tabs.items():
            if tab.file_path == file_path:
                self.tab_widget.setCurrentIndex(index)
                return

        view = self._open_new_tab(file_path)
        serialize.load(view, file_path)
        QtCore.QTimer.singleShot(0, lambda: self._update_preview_from_load(view))

    def get_focused_graph(self) -> Optional[GuiGraphView]:
        """
        Return the currently focused graph view.

        Returns:
            GuiGraphView | None: The active tab's graph view, or None if no
                tabs are open.
        """
        tab = self._tabs.get(self.tab_widget.currentIndex())
        if tab is None:
            return None

        return tab.graph_view

    def new_graph(self) -> None:
        self._open_new_tab(Path.home() / UNSAVED)
        sd = session.SessionData()
        sd.project_file = Path.home() / UNSAVED
        broker.emit(namespace.FILE_CHANGED, file_path=sd.project_file)

    def save_graph(self) -> None:
        tab = self._current_tab()
        if (
            tab.file_path == appdata.INITIAL_CATENA_FILE
            or tab.file_path.name == UNSAVED
        ):
            self.save_graph_as()
            return

        serialize.save(self.graph_view, tab.file_path)

    def save_graph_as(self) -> None:
        file_path = file.save_file_dialog(self)
        if file_path is None:
            return

        file_path.parent.mkdir(exist_ok=True, parents=True)

        tab = self._current_tab()
        tab.file_path = Path(file_path)

        index = self.tab_widget.currentIndex()
        self.tab_widget.setTabText(index, tab.file_path.stem)

        sd = session.SessionData()
        sd.project_file = tab.file_path
        sd.save()

        serialize.save(self.graph_view, tab.file_path)
        broker.emit(namespace.FILE_CHANGED, file_path=tab.file_path)

    def load_previous_graph(self) -> None:
        """Load the last saved graph into the current tab."""
        sd = session.SessionData()
        if not sd.project_file.exists():
            return

        tab = self._current_tab()
        tab.file_path = sd.project_file
        index = self.tab_widget.currentIndex()
        self.tab_widget.setTabText(index, sd.project_file.stem)

        serialize.load(self.graph_view, sd.project_file)
        QtCore.QTimer.singleShot(
            0, lambda: self._update_preview_from_load(self.graph_view)
        )
        broker.emit(namespace.FILE_CHANGED, file_path=sd.project_file)

    def load_graph(self) -> None:
        """Prompt the user for a catena graph file and load it in a new tab."""
        to_load = file.open_file_dialog(self)
        if to_load is None or not to_load.exists():
            return

        opened = [tab.file_path for tab in list(self._tabs.values())]
        if to_load in opened:
            return

        sd = session.SessionData()
        sd.project_file = to_load
        sd.save()

        view = self._open_new_tab(to_load)
        serialize.load(view, to_load)
        QtCore.QTimer.singleShot(0, lambda: self._update_preview_from_load(view))
        broker.emit(namespace.FILE_CHANGED, file_path=to_load)

    def _update_preview_from_load(self, view: GuiGraphView) -> None:
        for node in view._node_refs:
            if isinstance(node, WriteNode):
                node._emit_preview_update()

    def _create_subscriptions(self) -> None:
        broker.register_subscriber(namespace.FILE_NEW, self.new_graph)
        broker.register_subscriber(namespace.FILE_SAVE, self.save_graph)
        broker.register_subscriber(namespace.FILE_SAVE_AS, self.save_graph_as)
        broker.register_subscriber(namespace.FILE_LOAD, self.load_graph)
        broker.register_subscriber(
            namespace.FILE_UNDO, lambda: self.graph_view.commands.undo()
        )
        broker.register_subscriber(
            namespace.FILE_REDO, lambda: self.graph_view.commands.redo()
        )
        broker.register_subscriber(
            namespace.PREFERENCES_UPDATED, self._on_preferences_updated
        )
        broker.register_subscriber(namespace.GRAPH_OPEN_SUBGRAPH, self.open_subgraph)

    def _create_shortcuts(self) -> None:
        scm = shortcuts.ShortcutManager()

        redo_seq = QtGui.QKeySequence(QtGui.QKeySequence.StandardKey.Redo).toString()
        undo_seq = QtGui.QKeySequence(QtGui.QKeySequence.StandardKey.Undo).toString()
        copy_seq = QtGui.QKeySequence(QtGui.QKeySequence.StandardKey.Copy).toString()
        cut_seq = QtGui.QKeySequence(QtGui.QKeySequence.StandardKey.Cut).toString()
        paste_seq = QtGui.QKeySequence(QtGui.QKeySequence.StandardKey.Paste).toString()
        new_seq = QtGui.QKeySequence(QtGui.QKeySequence.StandardKey.New).toString()
        save_seq = QtGui.QKeySequence(QtGui.QKeySequence.StandardKey.Save).toString()
        save_as_seq = QtGui.QKeySequence(
            QtGui.QKeySequence.StandardKey.SaveAs
        ).toString()
        open_seq = QtGui.QKeySequence(QtGui.QKeySequence.StandardKey.Open).toString()

        scm.add_shortcut(
            action_name="New",
            key_sequence=new_seq,
            callback=self.new_graph,
            description="Start a new graph.",
            category="File",
        )
        scm.add_shortcut(
            action_name="Save",
            key_sequence=save_seq,
            callback=self.save_graph,
            description="Save current file.",
            category="File",
        )
        scm.add_shortcut(
            action_name="Save As",
            key_sequence=save_as_seq,
            callback=self.save_graph_as,
            description="Save current file as.",
            category="File",
        )
        scm.add_shortcut(
            action_name="Open",
            key_sequence=open_seq,
            callback=self.load_graph,
            description="Open a file.",
            category="File",
        )
        scm.add_shortcut(
            action_name="Redo",
            key_sequence=redo_seq,
            description="Redo the last action.",
            callback=lambda: self.graph_view.commands.redo(),
            category="Graph",
        )
        scm.add_shortcut(
            action_name="Undo",
            key_sequence=undo_seq,
            description="Undo the last action.",
            callback=lambda: self.graph_view.commands.undo(),
            category="Graph",
        )
        scm.add_shortcut(
            action_name="Delete Node",
            key_sequence="Del",
            description="Delete the current selected node(s).",
            callback=lambda: self.graph_view.delete_selected(),
            category="Graph",
        )
        scm.add_shortcut(
            action_name="Delete Node (Backspace)",
            key_sequence="Backspace",
            description="Delete the current selected node(s).",
            callback=lambda: self.graph_view.delete_selected(),
            category="Graph",
        )

        def _cut_selected() -> None:
            self.graph_view.copy_selected()
            self.graph_view.delete_selected()

        scm.add_shortcut(
            action_name="Copy Node",
            key_sequence=copy_seq,
            description="Copy selected nodes.",
            callback=lambda: self.graph_view.copy_selected(),
            category="Graph",
        )
        scm.add_shortcut(
            action_name="Cut Node",
            key_sequence=cut_seq,
            description="Cut selected nodes.",
            callback=_cut_selected,
            category="Graph",
        )
        scm.add_shortcut(
            action_name="Paste Node",
            key_sequence=paste_seq,
            description="Paste nodes from clipboard.",
            callback=lambda: self.graph_view.paste_clipboard(
                *self.graph_view.cursor_scene_pos()
            ),
            category="Graph",
        )

    def _apply_preferences_to_view(self, view: GuiGraphView) -> None:
        """Apply current preference values to a graph view."""
        graph_settings = Preferences().node_graph_preferences

        wire_style = (
            Nodes.WireStyle.BEZIER
            if graph_settings.wire_style == category_data.WIRE_STYLE_BEZIER
            else Nodes.WireStyle.RIGHT_ANGLE
        )
        view.set_wire_style(wire_style)

        view.grid_large = graph_settings.grid_size_large
        view.grid_small = graph_settings.grid_size_small
        view.color_grid_large = QtGui.QColor(graph_settings.color_grid_large)
        view.color_grid_small = QtGui.QColor(graph_settings.color_grid_small)
        view.color_bg = QtGui.QColor(graph_settings.color_grid_bg)

        view.zoom_step = graph_settings.zoom_step
        view.zoom_min = graph_settings.zoom_min
        view.zoom_max = graph_settings.zoom_max

        view.setBackgroundBrush(QtGui.QBrush(graph_settings.color_grid_bg))
        view.resetCachedContent()
        view.graph_scene.invalidate(
            view.sceneRect(),
            QtWidgets.QGraphicsScene.SceneLayer.BackgroundLayer,
        )

    def _on_preferences_updated(self) -> None:
        for tab in self._tabs.values():
            self._apply_preferences_to_view(tab.graph_view)
