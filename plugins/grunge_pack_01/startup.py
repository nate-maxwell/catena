import logging

from PySide6TK import Resources

from catena import api
from grunge_1 import Grunge1Node
from grunge_2 import Grunge2Node
from grunge_gradient import GrungeGradientNode

CATEGORY = "Grunge Pack 01"

logger = logging.getLogger(__name__)


def _add_node(node: type[api.CatenaNode], label: str) -> None:
    api.add_node_to_shelf(CATEGORY, node, label, Resources.BUTTON_PURPLE_40X40)


def build_shelf() -> None:
    logger.info("Building grunge pack shelf...")

    _add_node(GrungeGradientNode, "Grunge\nGrad")
    api.add_seperator_to_shelf(CATEGORY)
    _add_node(Grunge1Node, "Grunge\n1")
    _add_node(Grunge2Node, "Grunge\n2")


def build_registry() -> None:
    logger.info("Registering grunge pack nodes...")

    api.register_node(CATEGORY, GrungeGradientNode)
    api.register_node(CATEGORY, Grunge1Node)
    api.register_node(CATEGORY, Grunge2Node)


def initialize() -> None:
    build_shelf()
    build_registry()


initialize()
