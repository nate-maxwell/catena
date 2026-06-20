from pathlib import Path

import broker
from PySide6TK import Nodes
from PySide6TK import QtCore
from PySide6TK import QtGui
from PySide6TK import QtWidgets

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


class NodeGraphPane(DockablePane):
    pane_config = PaneConfig(
        title="Node Graph",
        default_area=QtCore.Qt.DockWidgetArea.BottomDockWidgetArea,
    )

    def __post_init__(self) -> None:
        self._create_shortcuts()
        self._create_subscriptions()
        self._on_preferences_updated()

    def create_widgets(self) -> None:
        self.graph_view = GuiGraphView(self)

    def create_layouts(self) -> None:
        self.content_layout.addWidget(self.graph_view)

    def new_graph(self) -> None:
        self.graph_view.clear()
        sd = session.SessionData()
        sd.project_file = Path.home() / "Unsaved.cg"
        broker.emit(namespace.FILE_CHANGED, file_path=sd.project_file)

    def save_graph(self) -> None:
        sd = session.SessionData()
        Nodes.save(self.graph_view, sd.project_file)

    def save_graph_as(self) -> None:
        file_path = file.save_file_dialog(self)
        if file_path is None:
            return

        file_path.parent.mkdir(exist_ok=True, parents=True)

        sd = session.SessionData()
        sd.project_file = Path(file_path)
        sd.save()

        Nodes.save(self.graph_view, sd.project_file)
        broker.emit(namespace.FILE_CHANGED, file_path=sd.project_file)

    def load_previous_graph(self) -> None:
        """Load the last saved graph."""
        sd = session.SessionData()
        if not sd.project_file.exists():
            return

        Nodes.load(self.graph_view, sd.project_file)
        QtCore.QTimer.singleShot(0, self._update_preview_from_load)
        broker.emit(namespace.FILE_CHANGED, file_path=sd.project_file)

    def load_graph(self) -> None:
        """Prompt the user for a catena graph file and load the selected graph."""
        sd = session.SessionData()

        to_load = file.open_file_dialog(self)
        if to_load is None or not to_load.exists():
            return  # TODO: Inform user of bad file!

        sd.project_file = to_load
        sd.save()

        Nodes.load(self.graph_view, sd.project_file)
        QtCore.QTimer.singleShot(0, self._update_preview_from_load)
        broker.emit(namespace.FILE_CHANGED, file_path=sd.project_file)

    def _update_preview_from_load(self) -> None:
        for node in self.graph_view._node_refs:
            if isinstance(node, WriteNode):
                node._emit_preview_update()

    def _create_subscriptions(self) -> None:
        broker.register_subscriber(namespace.FILE_NEW, self.new_graph)
        broker.register_subscriber(namespace.FILE_SAVE, self.save_graph)
        broker.register_subscriber(namespace.FILE_SAVE_AS, self.save_graph_as)
        broker.register_subscriber(namespace.FILE_LOAD, self.load_graph)
        broker.register_subscriber(namespace.FILE_UNDO, self.graph_view.commands.undo)
        broker.register_subscriber(namespace.FILE_REDO, self.graph_view.commands.redo)
        broker.register_subscriber(
            namespace.PREFERENCES_UPDATED, self._on_preferences_updated
        )

    def _create_shortcuts(self) -> None:
        # Shortcut Manager
        scm = shortcuts.ShortcutManager()

        # Defaults
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

        # Add shortcuts
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
            callback=self.graph_view.commands.redo,
            category="Graph",
        )
        scm.add_shortcut(
            action_name="Undo",
            key_sequence=undo_seq,
            description="Undo the last action.",
            callback=self.graph_view.commands.undo,
            category="Graph",
        )

        scm.add_shortcut(
            action_name="Delete Node",
            key_sequence="Del",
            description="Delete the current selected node(s).",
            callback=self.graph_view.delete_selected,
            category="Graph",
        )
        scm.add_shortcut(
            action_name="Delete Node (Backspace)",
            key_sequence="Backspace",
            description="Delete the current selected node(s).",
            callback=self.graph_view.delete_selected,
            category="Graph",
        )

        def _cut_selected() -> None:
            self.graph_view.copy_selected()
            self.graph_view.delete_selected()

        scm.add_shortcut(
            action_name="Copy Node",
            key_sequence=copy_seq,
            description="Copy selected nodes.",
            callback=self.graph_view.copy_selected,
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

    def _on_preferences_updated(self) -> None:
        graph_settings = Preferences().node_graph_preferences

        # -----Wire Style-----
        wire_style = (
            Nodes.WireStyle.BEZIER
            if graph_settings.wire_style == category_data.WIRE_STYLE_BEZIER
            else Nodes.WireStyle.RIGHT_ANGLE
        )
        self.graph_view.set_wire_style(wire_style)

        # -----Grid Values-----
        self.graph_view.grid_large = graph_settings.grid_size_large
        self.graph_view.grid_small = graph_settings.grid_size_small
        self.graph_view.color_grid_large = QtGui.QColor(graph_settings.color_grid_large)
        self.graph_view.color_grid_small = QtGui.QColor(graph_settings.color_grid_small)
        self.graph_view.color_bg = QtGui.QColor(graph_settings.color_grid_bg)

        # -----Zoom Values-----
        self.graph_view.zoom_step = graph_settings.zoom_step
        self.graph_view.zoom_min = graph_settings.zoom_min
        self.graph_view.zoom_max = graph_settings.zoom_max

        self.graph_view.setBackgroundBrush(QtGui.QBrush(graph_settings.color_grid_bg))
        self.graph_view.resetCachedContent()
        self.graph_view.scene().update()
        self.graph_view.graph_scene.invalidate(
            self.graph_view.sceneRect(),
            QtWidgets.QGraphicsScene.SceneLayer.BackgroundLayer,
        )
