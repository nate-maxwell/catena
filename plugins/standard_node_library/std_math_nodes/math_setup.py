import logging

from PySide6TK import Resources

from catena import api
from std_math_nodes.add import AddNode
from std_math_nodes.subtract import SubtractNode
from std_math_nodes.multiply import MultiplyNode
from std_math_nodes.divide import DivideNode
from std_math_nodes.min import MinNode
from std_math_nodes.max import MaxNode
from std_math_nodes.ceil import CeilNode
from std_math_nodes.floor import FloorNode
from std_math_nodes.screen import ScreenNode
from std_math_nodes.sin import SinNode
from std_math_nodes.cosine import CosineNode
from std_math_nodes.tan import TangentNode
from std_math_nodes.arctan import ArctangentNode

logger = logging.getLogger(__name__)

CATEGORY = "Math"


def _add_node(node: type[api.CatenaNode], label: str) -> None:
    api.add_node_to_shelf(CATEGORY, node, label, Resources.BUTTON_CYAN_40X40)


def build_shelf() -> None:
    logger.info("Building std math shelf...")

    _add_node(AddNode, "Add")
    _add_node(SubtractNode, "Sub")
    _add_node(MultiplyNode, "Mul")
    _add_node(DivideNode, "Div")
    api.add_seperator_to_shelf(CATEGORY)
    _add_node(MinNode, "Min")
    _add_node(MaxNode, "Max")
    _add_node(CeilNode, "Ceil")
    _add_node(FloorNode, "Floor")
    api.add_seperator_to_shelf(CATEGORY)
    _add_node(ScreenNode, "Screen")
    api.add_seperator_to_shelf(CATEGORY)
    _add_node(SinNode, "Sin")
    _add_node(CosineNode, "Cosine")
    _add_node(TangentNode, "Tan")
    _add_node(ArctangentNode, "Arctan")


def build_registry() -> None:
    logger.info("Registering std math nodes...")

    api.register_node(CATEGORY, AddNode)
    api.register_node(CATEGORY, ArctangentNode)
    api.register_node(CATEGORY, CeilNode)
    api.register_node(CATEGORY, CosineNode)
    api.register_node(CATEGORY, DivideNode)
    api.register_node(CATEGORY, FloorNode)
    api.register_node(CATEGORY, MaxNode)
    api.register_node(CATEGORY, MinNode)
    api.register_node(CATEGORY, MultiplyNode)
    api.register_node(CATEGORY, ScreenNode)
    api.register_node(CATEGORY, SinNode)
    api.register_node(CATEGORY, SubtractNode)
    api.register_node(CATEGORY, TangentNode)


def initialize() -> None:
    build_shelf()
    build_registry()
