from PySide6TK.Nodes import FieldDefinition
from PySide6TK.Nodes import FieldType
from PySide6TK.Nodes import Port
from PySide6TK.Nodes import PortType

from catena.nodes.data import PortDataType
from catena.nodes.data import DATA_TYPE_COLORS
from catena.nodes.data import FIELD_PORT_DATA_TYPES
from catena.nodes.data import TEXTURE_DATA_TYPES
from catena.nodes.node_registry import NodeRegistry

from catena.nodes.node_gui import CatenaNode

__all__ = [
    "CatenaNode",
    "DATA_TYPE_COLORS",
    "FieldDefinition",
    "FieldType",
    "FIELD_PORT_DATA_TYPES",
    "PortDataType",
    "Port",
    "PortType",
    "TEXTURE_DATA_TYPES",
    "register_node",
    "node_registry_to_dict",
]

_node_registry = NodeRegistry()


def register_node(category: str, node_cls: type[CatenaNode]) -> None:
    """
    Registers the given node class to the specified category.
    If the category does not exist, it is created.

    Args:
        category (str): Which category to register the node to.
        node_cls (str): The node class type to register, not a node instance.
    """
    _node_registry.register_node(category, node_cls)


def node_registry_to_dict() -> dict:
    """
    Returns a dictionary of string categories to lists of node classes,
    representing the current snapshot of the node registry.
    """
    return _node_registry.to_dict()
