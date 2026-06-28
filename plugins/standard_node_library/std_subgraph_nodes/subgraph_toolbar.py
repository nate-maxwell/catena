from PySide6TK import Resources

from catena import api
from std_subgraph_nodes.input import GraphInputNode
from std_subgraph_nodes.output import GraphOutputNode
from std_subgraph_nodes.subgraph import SubgraphNode


def _add_node(node: type[api.CatenaNode], label: str) -> None:
    api.add_node_to_toolbar("Subgraph", node, label, Resources.BUTTON_BLACK_40X40)


def build_shelf() -> None:
    _add_node(SubgraphNode, "Sub\nGraph")

    api.add_seperator_to_toolbar("Subgraph")

    _add_node(GraphInputNode, "Input")
    _add_node(GraphOutputNode, "Output")
