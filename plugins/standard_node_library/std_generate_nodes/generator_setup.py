import logging

from PySide6TK import Resources

from catena import api
from std_generate_nodes.blue_noise import BlueNoiseNode
from std_generate_nodes.bnw_spots import BNWSpotsNode
from std_generate_nodes.cells import CellsNode
from std_generate_nodes.clouds import CloudsNode
from std_generate_nodes.fibers import FibersNode
from std_generate_nodes.pink_noise import PinkNoiseNode
from std_generate_nodes.perlin_noise import PerlinNoiseNode
from std_generate_nodes.white_noise import WhiteNoiseNode
from std_generate_nodes.voronoi_noise import VoronoiNoiseNode
from std_generate_nodes.directional_noise import DirectionalNoiseNode
from std_generate_nodes.color import ColorNode
from std_generate_nodes.float import FloatNode
from std_generate_nodes.integer import IntegerNode
from std_generate_nodes.gradient import GradientNode
from std_generate_nodes.checker import CheckerNode
from std_generate_nodes.polygon import PolygonNode
from std_generate_nodes.shape import ShapeNode
from std_generate_nodes.grunge import GrungeNode
from std_generate_nodes.mold import MoldNode
from std_generate_nodes.scratches import ScratchesNode
from std_generate_nodes.weave import WeaveNode

logger = logging.getLogger(__name__)

CATEGORY = "Generator"


def _add_node(node: type[api.CatenaNode], label: str) -> None:
    api.add_node_to_shelf(CATEGORY, node, label, Resources.BUTTON_PURPLE_40X40)


def build_shelf() -> None:
    logger.info("Building std generator shelf...")

    _add_node(BlueNoiseNode, "Blue\nNoise")
    _add_node(BNWSpotsNode, "BnW\nSpots")
    _add_node(CellsNode, "Cells")
    _add_node(CloudsNode, "Clouds")
    _add_node(DirectionalNoiseNode, "Dir\nNoise")
    _add_node(FibersNode, "Fibers")
    _add_node(PinkNoiseNode, "Pink\nNoise")
    _add_node(PerlinNoiseNode, "Perlin\nNoise")
    _add_node(WhiteNoiseNode, "White\nNoise")
    _add_node(VoronoiNoiseNode, "Voronoi")
    api.add_seperator_to_shelf(CATEGORY)
    _add_node(ColorNode, "Color")
    _add_node(FloatNode, "Float")
    _add_node(IntegerNode, "Int")
    _add_node(GradientNode, "Grad")
    _add_node(CheckerNode, "Checker")
    _add_node(PolygonNode, "Poly")
    _add_node(ShapeNode, "Shape")
    api.add_seperator_to_shelf(CATEGORY)
    _add_node(GrungeNode, "Grunge")
    _add_node(MoldNode, "Mold")
    api.add_seperator_to_shelf(CATEGORY)
    _add_node(ScratchesNode, "Scratch")
    _add_node(WeaveNode, "Weave")


def build_registry() -> None:
    logger.info("Registering std generator nodes...")

    api.register_node(CATEGORY, BlueNoiseNode)
    api.register_node(CATEGORY, BNWSpotsNode)
    api.register_node(CATEGORY, CellsNode)
    api.register_node(CATEGORY, CheckerNode)
    api.register_node(CATEGORY, CloudsNode)
    api.register_node(CATEGORY, ColorNode)
    api.register_node(CATEGORY, DirectionalNoiseNode)
    api.register_node(CATEGORY, FibersNode)
    api.register_node(CATEGORY, FloatNode)
    api.register_node(CATEGORY, GradientNode)
    api.register_node(CATEGORY, GrungeNode)
    api.register_node(CATEGORY, IntegerNode)
    api.register_node(CATEGORY, MoldNode)
    api.register_node(CATEGORY, PerlinNoiseNode)
    api.register_node(CATEGORY, PinkNoiseNode)
    api.register_node(CATEGORY, PolygonNode)
    api.register_node(CATEGORY, ScratchesNode)
    api.register_node(CATEGORY, ShapeNode)
    api.register_node(CATEGORY, VoronoiNoiseNode)
    api.register_node(CATEGORY, WeaveNode)
    api.register_node(CATEGORY, WhiteNoiseNode)


def initialize() -> None:
    build_shelf()
    build_registry()
