import logging

from PySide6TK import Resources

from catena import api
from std_convert_nodes.split import SplitNode
from std_convert_nodes.append import AppendNode
from std_convert_nodes.height_to_ao import HeightToAONode
from std_convert_nodes.height_to_normal import HeightToNormalNode
from std_convert_nodes.normal_to_vec4 import NormalToVector4Node
from std_convert_nodes.int_to_float import IntToFloatNode
from std_convert_nodes.int_to_vec4 import IntToVec4Node
from std_convert_nodes.float_to_int import FloatToIntNode
from std_convert_nodes.float_to_vec4 import FloatToVec4Node

logger = logging.getLogger(__name__)

CATEGORY = "Convert"


def _add_node(node: type[api.CatenaNode], label: str) -> None:
    api.add_node_to_shelf(CATEGORY, node, label, Resources.BUTTON_BLUE_40X40)


def build_shelf() -> None:
    logger.info("Building std convert shelf...")

    _add_node(SplitNode, "Split")
    _add_node(AppendNode, "Append")
    api.add_seperator_to_shelf(CATEGORY)
    _add_node(HeightToAONode, "Height\nto\nAO")
    _add_node(HeightToNormalNode, "Vec4\nto\nNormal")
    _add_node(NormalToVector4Node, "Normal\nto\nVec4")
    api.add_seperator_to_shelf(CATEGORY)
    _add_node(IntToFloatNode, "Int\nto\nFloat")
    _add_node(IntToVec4Node, "Int\nto\nVec4")
    _add_node(FloatToIntNode, "Float\nto\nInt")
    _add_node(FloatToVec4Node, "Float\nto\nVec4")


def build_registry() -> None:
    logger.info("Registering std convert nodes...")
    api.register_node(CATEGORY, AppendNode)
    api.register_node(CATEGORY, HeightToAONode)
    api.register_node(CATEGORY, HeightToNormalNode)
    api.register_node(CATEGORY, NormalToVector4Node)
    api.register_node(CATEGORY, SplitNode)

    api.register_node(CATEGORY, IntToFloatNode)
    api.register_node(CATEGORY, IntToVec4Node)
    api.register_node(CATEGORY, FloatToIntNode)
    api.register_node(CATEGORY, FloatToVec4Node)


def initialize() -> None:
    build_shelf()
    build_registry()
