import logging

from PySide6TK import Resources

from catena import api
from cells_1 import Cells1Node
from cells_2 import Cells2Node
from cells_3 import Cells3Node
from dirt_1 import Dirt1Node
from dirt_2 import Dirt2Node
from moisture_noise import MoistureNoiseNode
from fractal_sum_base import FractalSumBaseNode
from fractal_sum_1 import FractalSum1Node
from fractal_sum_2 import FractalSum2Node
from fractal_sum_3 import FractalSum3Node

CATEGORY = "Noise Pack 01"

logger = logging.getLogger(__name__)


def _add_node(node: type[api.CatenaNode], label: str) -> None:
    api.add_node_to_shelf(CATEGORY, node, label, Resources.BUTTON_PURPLE_40X40)


def build_shelf() -> None:
    logger.info("Building noise pack shelf...")

    _add_node(Cells1Node, "Cells\n1")
    _add_node(Cells2Node, "Cells\n2")
    _add_node(Cells3Node, "Cells\n3")

    api.add_seperator_to_shelf(CATEGORY)

    _add_node(Dirt1Node, "Dirt\n1")
    _add_node(Dirt1Node, "Dirt\n2")

    api.add_seperator_to_shelf(CATEGORY)

    _add_node(FractalSumBaseNode, "Fractal\nSum\nBase")
    _add_node(FractalSum1Node, "Fractal\nSum\n1")
    _add_node(FractalSum2Node, "Fractal\nSum\n2")
    _add_node(FractalSum3Node, "Fractal\nSum\n3")

    api.add_seperator_to_shelf(CATEGORY)

    _add_node(MoistureNoiseNode, "Moistur\nNoise")


def build_registry() -> None:
    logger.info("Registering noise pack nodes...")

    api.register_node(CATEGORY, Cells1Node)
    api.register_node(CATEGORY, Cells2Node)
    api.register_node(CATEGORY, Cells3Node)
    api.register_node(CATEGORY, Dirt1Node)
    api.register_node(CATEGORY, Dirt2Node)
    api.register_node(CATEGORY, FractalSumBaseNode)
    api.register_node(CATEGORY, FractalSum1Node)
    api.register_node(CATEGORY, FractalSum2Node)
    api.register_node(CATEGORY, FractalSum3Node)
    api.register_node(CATEGORY, MoistureNoiseNode)


def initialize() -> None:
    build_shelf()
    build_registry()


initialize()
