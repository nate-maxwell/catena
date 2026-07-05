from pathlib import Path

from catena.nodes.node import CatenaNode
from catena.panes.node_graph import NodeGraphPane

__all__ = ["add_to_focussed", "open_file"]

_graph_pane: NodeGraphPane | None = None


def init_graph_pane(graph_pane: NodeGraphPane | None = None) -> None:
    """
    Used by the client at startup to inject the graph pane which manages all
    opened graphs.
    """
    global _graph_pane
    if graph_pane is None:
        return

    _graph_pane = graph_pane


def add_to_focussed(node: type[CatenaNode]) -> None:
    """
    Creates an instance of the given node class type to the currently focused
    graph.
    """
    if graph_view := _graph_pane.get_focused_graph():
        coords = graph_view.view_center()
        graph_view.add_node(node=node(), x=coords.x(), y=coords.y())


def open_file(filepath: Path) -> None:
    """
    Open the specific filepath in a new graph.
    Skips if the graph is already open.

    If file is opened, filepath is emitted over channel "client.file.changed".
    """
    _graph_pane.load_filepath(Path(filepath))
