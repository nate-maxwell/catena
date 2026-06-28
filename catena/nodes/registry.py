from collections import defaultdict
from typing import Any
from typing import Optional

from catena.nodes.node import CatenaNode


class NodeRegistry(object):
    """
    Singleton container holding all registered nodes in the current application
    runtime.

    Graphs reference this registry to build context menus and understand metrics
    about the overall available node pool.
    """

    _instance: Optional["NodeRegistry"] = None

    def __new__(cls, *args: Any, **kwargs: Any) -> "NodeRegistry":
        if cls._instance is None:
            cls._instance = super(NodeRegistry, cls).__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        # Prevent re-initialization on subsequent calls
        if getattr(self, "_initialized", False):
            return
        self._initialized = True

        self._node_table: dict[str, set[type[CatenaNode]]] = defaultdict(set)

    def register_node(self, category: str, node_cls: type[CatenaNode]) -> None:
        """
        Registers the given node class to the specified category.
        If the category does not exist, it is created.

        Args:
            category (str): Which category to register the node to.
            node_cls (str): The node class type to register, not a node instance.
        """
        self._node_table[category].add(node_cls)

    def to_dict(self) -> dict:
        """
        Returns a dictionary of string categories to lists of node classes,
        representing the current snapshot of the node registry.
        """
        data = {}

        for category, nodes in self._node_table.items():
            value = sorted(nodes, key=lambda n: n.__name__)  # alphabetically sorted
            data[category] = value

        return data
