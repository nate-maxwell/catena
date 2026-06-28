import logging

from PySide6TK import Resources

from catena import api
from std_subgraph_nodes.input import GraphInputNode
from std_subgraph_nodes.output import GraphOutputNode
from std_subgraph_nodes.subgraph import SubgraphNode

logger = logging.getLogger(__name__)

CATEGORY = "Subgraph"


def _add_node(node: type[api.CatenaNode], label: str) -> None:
    api.add_node_to_shelf(CATEGORY, node, label, Resources.BUTTON_BLACK_40X40)


def build_shelf() -> None:
    logger.info("Registering std subgraph shelf...")

    _add_node(SubgraphNode, "Sub\nGraph")
    api.add_seperator_to_shelf(CATEGORY)
    _add_node(GraphInputNode, "Input")
    _add_node(GraphOutputNode, "Output")


def build_registry() -> None:
    logger.info("Registering std subgraph nodes...")
    api.register_node(CATEGORY, SubgraphNode)
    api.register_node(CATEGORY, GraphInputNode)
    api.register_node(CATEGORY, GraphOutputNode)


def initialize() -> None:
    build_shelf()
    build_registry()
