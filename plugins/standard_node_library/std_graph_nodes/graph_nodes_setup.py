import logging
from typing import Callable

from PySide6TK import Resources

from catena import api
from std_graph_nodes.comparison import ComparisonNode
from std_graph_nodes.read import ReadNode
from std_graph_nodes.switch import SwitchNode
from std_graph_nodes.write import WriteNode
from std_graph_nodes.input import GraphInputNode
from std_graph_nodes.output import GraphOutputNode
from std_graph_nodes.subgraph import SubgraphNode

logger = logging.getLogger(__name__)

CATEGORY = "Graph"


def _add_node(node: type[api.CatenaNode], label: str) -> None:
    api.add_node_to_shelf(CATEGORY, node, label, Resources.BUTTON_BLACK_40X40)


def _add_cmd(cmd: Callable, label: str) -> None:
    api.add_shelf_command(CATEGORY, cmd, label, Resources.BUTTON_BLACK_40X40)


def build_shelf() -> None:
    logger.info("Building std graph shelf...")

    _add_node(ReadNode, "Read")
    _add_node(WriteNode, "Write")
    api.add_seperator_to_shelf(CATEGORY)
    _add_node(ComparisonNode, "Compar")
    _add_node(SwitchNode, "Switch")
    api.add_seperator_to_shelf(CATEGORY)
    _add_node(SubgraphNode, "Sub\nGraph")
    _add_node(GraphInputNode, "Input")
    _add_node(GraphOutputNode, "Output")


def build_registry() -> None:
    logger.info("Registering std graph nodes...")
    api.register_node(CATEGORY, ComparisonNode)
    api.register_node(CATEGORY, GraphInputNode)
    api.register_node(CATEGORY, GraphOutputNode)
    api.register_node(CATEGORY, ReadNode)
    api.register_node(CATEGORY, SubgraphNode)
    api.register_node(CATEGORY, SwitchNode)
    api.register_node(CATEGORY, WriteNode)


def initialize() -> None:
    build_shelf()
    build_registry()
