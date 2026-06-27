from catena import api

from PySide6TK import Resources

from std_flood_fill_nodes.flood_fill import FloodFillNode
from std_flood_fill_nodes.ff_to_gradient import FloodFillToGradientNode
from std_flood_fill_nodes.ff_to_greyscale import FloodFillToGreyscaleNode
from std_flood_fill_nodes.ff_to_rand_color import FloodFillToRandomColorNode


def _add_node(node: type[api.CatenaNode], label: str) -> None:
    api.add_node_to_toolbar("Flood Fill", node, label, Resources.BUTTON_MAGENTA_40X40)


def build_shelf() -> None:
    _add_node(FloodFillNode, "Flood\nFill")

    api.add_seperator_to_toolbar("Flood Fill")

    _add_node(FloodFillToGradientNode, "FF To\nGrad")
    _add_node(FloodFillToGreyscaleNode, "FF To\nGrey")
    _add_node(FloodFillToRandomColorNode, "FF To\nRand\nColor")
