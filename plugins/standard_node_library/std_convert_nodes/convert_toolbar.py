from catena import api

from PySide6TK import Resources

from std_convert_nodes.split import SplitNode
from std_convert_nodes.append import AppendNode
from std_convert_nodes.height_to_ao import HeightToAONode
from std_convert_nodes.height_to_normal import HeightToNormalNode
from std_convert_nodes.normal_to_vec4 import NormalToVector4Node
from std_convert_nodes.int_to_float import IntToFloatNode
from std_convert_nodes.int_to_vec4 import IntToVec4Node
from std_convert_nodes.float_to_int import FloatToIntNode
from std_convert_nodes.float_to_vec4 import FloatToVec4Node


def _add_node(node: type[api.CatenaNode], label: str) -> None:
    api.add_node_to_toolbar("Convert", node, label, Resources.BUTTON_BLUE_40X40)


def build_shelf() -> None:
    _add_node(SplitNode, "Split")
    _add_node(AppendNode, "Append")

    api.add_seperator_to_toolbar("Convert")

    _add_node(HeightToAONode, "Height\nto\nAO")
    _add_node(HeightToNormalNode, "Vec4\nto\nNormal")
    _add_node(NormalToVector4Node, "Normal\nto\nVec4")

    api.add_seperator_to_toolbar("Convert")

    _add_node(IntToFloatNode, "Int\nto\nFloat")
    _add_node(IntToVec4Node, "Int\nto\nVec4")
    _add_node(FloatToIntNode, "Float\nto\nInt")
    _add_node(FloatToVec4Node, "Float\nto\nVec4")
