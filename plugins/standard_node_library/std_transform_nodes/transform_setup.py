import logging

from PySide6TK import Resources

from catena import api
from std_transform_nodes.flip import FlipNode
from std_transform_nodes.offset import OffsetNode
from std_transform_nodes.rotate_scale import RotateScaleNode
from std_transform_nodes.scatter import ScatterNode
from std_transform_nodes.tile import TileNode
from std_transform_nodes.warp import WarpNode
from std_transform_nodes.warp_directional import DirectionalWarpNode
from std_transform_nodes.warp_vector import VectorWarpNode

logger = logging.getLogger(__name__)

CATEGORY = "Transform"


def _add_node(node: type[api.CatenaNode], label: str) -> None:
    api.add_node_to_shelf(CATEGORY, node, label, Resources.BUTTON_GREEN_40X40)


def build_shelf() -> None:
    logger.info("Building std transform shelf...")

    _add_node(FlipNode, "Flip")
    _add_node(OffsetNode, "Offset")
    _add_node(RotateScaleNode, "Rotate\nScale")
    api.add_seperator_to_shelf(CATEGORY)
    _add_node(ScatterNode, "Scatter")
    _add_node(TileNode, "Tile")
    api.add_seperator_to_shelf(CATEGORY)
    _add_node(WarpNode, "Warp")
    _add_node(DirectionalWarpNode, "Dir\nWarp")
    _add_node(VectorWarpNode, "Vector\nWarp")


def build_registry() -> None:
    logger.info("Registering std transform nodes...")

    api.register_node(CATEGORY, DirectionalWarpNode)
    api.register_node(CATEGORY, FlipNode)
    api.register_node(CATEGORY, OffsetNode)
    api.register_node(CATEGORY, RotateScaleNode)
    api.register_node(CATEGORY, ScatterNode)
    api.register_node(CATEGORY, TileNode)
    api.register_node(CATEGORY, VectorWarpNode)
    api.register_node(CATEGORY, WarpNode)


def initialize() -> None:
    build_shelf()
    build_registry()
