from pathlib import Path

from PySide6TK import Resources

from catena.nodes.node_gui import CatenaNode
from catena.panes.node_graph.node_graph import NodeGraphPane
from catena.toolbars.actions_toolbar import EditorActionToolbar

__all__ = ["add_to_focussed", "add_node_to_toolbar", "add_seperator_to_toolbar"]

_graph_pane: NodeGraphPane | None = None


def init_graph_pane(graph_pane: NodeGraphPane | None = None) -> None:
    global _graph_pane
    if graph_pane is None:
        return

    _graph_pane = graph_pane


def add_to_focussed(node: type[CatenaNode]) -> None:
    if graph_view := _graph_pane.get_focused_graph():
        coords = graph_view.view_center()
        graph_view.add_node(node=node(), x=coords.x(), y=coords.y())


_editor_actions_toolbar: EditorActionToolbar | None = None


def init_actions_toolbar_ref(toolbar: EditorActionToolbar | None = None) -> None:
    global _editor_actions_toolbar
    if toolbar is None:
        return

    _editor_actions_toolbar = toolbar


def add_node_to_toolbar(
    toolbar: str,
    node: type[CatenaNode],
    label: str,
    icon_path: Path = Resources.BUTTON_WHITE_40X40,
) -> None:
    """
    Adds a node to the toolbar by the given name. If a toolbar cannot be found by
    that name, one is constructed and the button is added to that.

    Args:
        toolbar (str):
        node (type[CatenaNode]):
        label (str):
        icon_path (pathlib.Path):
    """
    _editor_actions_toolbar.add_node(toolbar, node, label, icon_path)


def add_seperator_to_toolbar(toolbar: str) -> None:
    """Add a spacing seperator to the toolbar of the given name."""
    _editor_actions_toolbar.add_seperator(toolbar)
