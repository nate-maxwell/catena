from PySide6TK import QtCore
from PySide6TK import QtGui

from catena.core import shortcuts
from catena.core.nodes.graph import CatenaGraphView
from catena.core.panes.pane import DockablePane
from catena.core.panes.pane import PaneConfig


class NodeGraphPane(DockablePane):
    pane_config = PaneConfig(
        title="Node Graph",
        default_area=QtCore.Qt.DockWidgetArea.BottomDockWidgetArea,
    )

    def __post_init__(self) -> None:
        self.create_shortcuts()

    def create_widgets(self) -> None:
        self.graph_view = CatenaGraphView(self)

    def create_layouts(self) -> None:
        self.content_layout.addWidget(self.graph_view)

    def create_shortcuts(self) -> None:
        # Shortcut Manager
        scm = shortcuts.ShortcutManager()

        # Defaults
        redo_seq = QtGui.QKeySequence(QtGui.QKeySequence.StandardKey.Redo).toString()
        undo_seq = QtGui.QKeySequence(QtGui.QKeySequence.StandardKey.Undo).toString()
        copy_seq = QtGui.QKeySequence(QtGui.QKeySequence.StandardKey.Copy).toString()
        paste_seq = QtGui.QKeySequence(QtGui.QKeySequence.StandardKey.Paste).toString()

        # Add shortcuts
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
