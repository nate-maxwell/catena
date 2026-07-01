import logging

from PySide6TK import Resources

from catena import api
from moisture_noise import MoistureNoiseNode
from fractal_sum_base import FractalSumBaseNode
from fractal_sum_1 import FractalSum01Node
from fractal_sum_2 import FractalSum02Node
from fractal_sum_3 import FractalSum03Node

CATEGORY = "Noise Pack 01"

logger = logging.getLogger(__name__)


def _add_node(node: type[api.CatenaNode], label: str) -> None:
    api.add_node_to_shelf(CATEGORY, node, label, Resources.BUTTON_PURPLE_40X40)


def build_shelf() -> None:
    logger.info("Building noise pack shelf...")

    _add_node(FractalSumBaseNode, "Fractal\nSum\nBase")
    _add_node(FractalSum01Node, "Fractal\nSum\n1")
    _add_node(FractalSum02Node, "Fractal\nSum\n2")
    _add_node(FractalSum03Node, "Fractal\nSum\n3")

    api.add_seperator_to_shelf(CATEGORY)

    _add_node(MoistureNoiseNode, "Moistur\nNoise")


def build_registry() -> None:
    logger.info("Registering noise pack nodes...")

    api.register_node(CATEGORY, FractalSumBaseNode)
    api.register_node(CATEGORY, FractalSum01Node)
    api.register_node(CATEGORY, FractalSum02Node)
    api.register_node(CATEGORY, FractalSum03Node)
    api.register_node(CATEGORY, MoistureNoiseNode)


def initialize() -> None:
    build_shelf()
    build_registry()


initialize()
