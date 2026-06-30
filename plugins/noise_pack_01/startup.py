import logging

from PySide6TK import Resources

from catena import api
from moisture_noise import MoistureNoiseNode
from fractal_sum_base import FractalSumBaseNode

CATEGORY = "Noise Pack 01"

logger = logging.getLogger(__name__)


def _add_node(node: type[api.CatenaNode], label: str) -> None:
    api.add_node_to_shelf(CATEGORY, node, label, Resources.BUTTON_PURPLE_40X40)


def build_shelf() -> None:
    logger.info("Building noise pack shelf...")

    _add_node(FractalSumBaseNode, "Fractal\nSum\nBase")
    _add_node(MoistureNoiseNode, "Moistur\nNoise")


def build_registry() -> None:
    logger.info("Registering noise pack nodes...")

    api.register_node(CATEGORY, FractalSumBaseNode)
    api.register_node(CATEGORY, MoistureNoiseNode)


def initialize() -> None:
    build_shelf()
    build_registry()


initialize()
