import logging

from PySide6TK import Resources

from catena import api
from std_flood_fill_nodes.flood_fill import FloodFillNode
from std_flood_fill_nodes.ff_to_bbox import FloodFillToBBoxNode
from std_flood_fill_nodes.ff_to_gradient import FloodFillToGradientNode
from std_flood_fill_nodes.ff_to_greyscale import FloodFillToGreyscaleNode
from std_flood_fill_nodes.ff_to_rand_color import FloodFillToRandomColorNode

logger = logging.getLogger(__name__)

CATEGORY = "Flood Fill"


def _add_node(node: type[api.CatenaNode], label: str) -> None:
    api.add_node_to_shelf(CATEGORY, node, label, Resources.BUTTON_MAGENTA_40X40)


def build_shelf() -> None:
    logger.info("Building std floodfill shelf...")

    _add_node(FloodFillNode, "Flood\nFill")

    api.add_seperator_to_shelf(CATEGORY)

    _add_node(FloodFillToBBoxNode, "FF To\nBBox")
    _add_node(FloodFillToGradientNode, "FF To\nGrad")
    _add_node(FloodFillToGreyscaleNode, "FF To\nGrey")
    _add_node(FloodFillToRandomColorNode, "FF To\nRand\nColor")


def build_registry() -> None:
    logger.info("Registering std floodfill nodes...")
    api.register_node(CATEGORY, FloodFillNode)
    api.register_node(CATEGORY, FloodFillToBBoxNode)
    api.register_node(CATEGORY, FloodFillToGradientNode)
    api.register_node(CATEGORY, FloodFillToGreyscaleNode)
    api.register_node(CATEGORY, FloodFillToRandomColorNode)


def initialize() -> None:
    build_shelf()
    build_registry()
