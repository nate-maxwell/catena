from catena.nodes.node_gui import CatenaNode
from catena.panes.node_graph.node_graph import NodeGraphPane

__all__ = ["add_to_focussed"]

_graph_pane: NodeGraphPane | None = None


def init_graph_pane(graph_pane: NodeGraphPane | None = None) -> None:
    global _graph_pane
    if graph_pane is None:
        return

    _graph_pane = graph_pane


def add_to_focussed(node: type[CatenaNode]) -> None:
    if graph_view := _graph_pane.get_focused_graph():
        graph_view.add_node_to_center(node())
