import broker
from PySide6TK import QtCore
from PySide6TK import QtGui
from PySide6TK import Nodes

from catena.core import shortcuts
from catena.core.nodes.graph import CatenaGraphView
from catena.core.panes.pane import DockablePane
from catena.core.panes.pane import PaneConfig
from catena.core import appdata
from catena.core import namespace


class NodeGraphPane(DockablePane):
    pane_config = PaneConfig(
        title="Node Graph",
        default_area=QtCore.Qt.DockWidgetArea.BottomDockWidgetArea,
    )

    def __post_init__(self) -> None:
        self._create_shortcuts()
        self._create_subscriptions()

    def create_widgets(self) -> None:
        self.graph_view = CatenaGraphView(self)

    def create_layouts(self) -> None:
        self.content_layout.addWidget(self.graph_view)

    def save_graph(self) -> None:
        Nodes.save(self.graph_view, appdata.CATENA_GRAPH_FILE)

    def load_graph(self) -> None:
        if not appdata.CATENA_GRAPH_FILE.exists():
            return

        Nodes.load(self.graph_view, appdata.CATENA_GRAPH_FILE)

    def _create_subscriptions(self) -> None:
        broker.register_subscriber(namespace.CLIENT_SAVE, self.save_graph)
        broker.register_subscriber(namespace.CLIENT_UNDO, self.graph_view.commands.undo)
        broker.register_subscriber(namespace.CLIENT_REDO, self.graph_view.commands.redo)

    def _create_shortcuts(self) -> None:
        # Shortcut Manager
        scm = shortcuts.ShortcutManager()

        # Defaults
        redo_seq = QtGui.QKeySequence(QtGui.QKeySequence.StandardKey.Redo).toString()
        undo_seq = QtGui.QKeySequence(QtGui.QKeySequence.StandardKey.Undo).toString()
        copy_seq = QtGui.QKeySequence(QtGui.QKeySequence.StandardKey.Copy).toString()
        paste_seq = QtGui.QKeySequence(QtGui.QKeySequence.StandardKey.Paste).toString()

        # Add shortcuts
        scm.add_shortcut(
            action_name="Save",
            key_sequence="Ctrl+S",
            callback=self.save_graph,
            description="Save current project.",
            category="File",
        )

        scm.add_shortcut(
            action_name="Redo",
            key_sequence=redo_seq,
            description="Redo the last action.",
            callback=self.graph_view.commands.redo,
        )
        scm.add_shortcut(
            action_name="Undo",
            key_sequence=undo_seq,
            description="Undo the last action.",
            callback=self.graph_view.commands.undo,
        )

        scm.add_shortcut(
            action_name="Delete Node",
            key_sequence="Del",
            description="Delete the current selected node(s).",
            callback=self.graph_view.delete_selected,
        )
        scm.add_shortcut(
            action_name="Delete Node (Backspace)",
            key_sequence="Backspace",
            description="Delete the current selected node(s).",
            callback=self.graph_view.delete_selected,
        )

        scm.add_shortcut(
            action_name="Copy Node",
            key_sequence=copy_seq,
            description="Copy selected nodes.",
            callback=self.graph_view.copy_selected,
        )
        scm.add_shortcut(
            action_name="Paste Node",
            key_sequence=paste_seq,
            description="Paste nodes from clipboard.",
            callback=lambda: self.graph_view.paste_clipboard(
                *self.graph_view.cursor_scene_pos()
            ),
        )
