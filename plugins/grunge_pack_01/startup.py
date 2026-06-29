import logging

from PySide6TK import Resources

from catena import api
from moisture_noise import MoistureNoiseNode
from grunge_01 import Grunge01Node
from grunge_02 import Grunge02Node

CATEGORY = "Grunge Pack 01"

logger = logging.getLogger(__name__)


def _add_node(node: type[api.CatenaNode], label: str) -> None:
    api.add_node_to_shelf(CATEGORY, node, label, Resources.BUTTON_PURPLE_40X40)


def build_shelf() -> None:
    logger.info("Building grunge pack shelf...")

    _add_node(MoistureNoiseNode, "Moistur\nNoise")
    api.add_seperator_to_shelf(CATEGORY)
    _add_node(Grunge01Node, "Grunge\n01")
    _add_node(Grunge02Node, "Grunge\n02")


def build_registry() -> None:
    logger.info("Registering grunge pack nodes...")

    api.register_node(CATEGORY, Grunge01Node)
    api.register_node(CATEGORY, Grunge02Node)
    api.register_node(CATEGORY, MoistureNoiseNode)


def initialize() -> None:
    build_shelf()
    build_registry()


initialize()
