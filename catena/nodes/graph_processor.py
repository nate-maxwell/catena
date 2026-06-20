import json
from pathlib import Path
from typing import Any
from typing import Optional
from typing import Type
from typing import TypeVar
import importlib
import inspect
import pkgutil

import numpy

import catena.nodes as nodes_package
from catena.nodes.node_processor import ProcessorNode
from catena.nodes.file.write import WriteProcessor

T = TypeVar("T", bound=ProcessorNode)

_NODE_TYPE_REGISTRY: dict[str, Type[ProcessorNode]] = {}

_registry_initialized: bool = False


def auto_register_processors() -> None:
    """
    Scan all modules in catena.nodes and automatically register every
    ProcessorNode subclass under the corresponding node type name.

    Assumes the convention that XxxProcessor corresponds to XxxNode —
    e.g. BlurProcessor is registered under "BlurNode".
    """
    global _registry_initialized
    if _registry_initialized:
        return
    _registry_initialized = True

    for finder, module_name, _ in pkgutil.walk_packages(
        path=nodes_package.__path__,
        prefix=nodes_package.__name__ + ".",
        onerror=lambda x: None,
    ):
        try:
            module = importlib.import_module(module_name)
        except Exception:
            continue

        for _, obj in inspect.getmembers(module, inspect.isclass):
            if (
                issubclass(obj, ProcessorNode)
                and obj is not ProcessorNode
                and obj.__module__ == module_name
            ):
                node_type_name = obj.__name__.replace("Processor", "Node")
                _NODE_TYPE_REGISTRY[node_type_name] = obj

    _NODE_TYPE_REGISTRY["AlbedoNode"] = WriteProcessor
    _NODE_TYPE_REGISTRY["NormalNode"] = WriteProcessor
    _NODE_TYPE_REGISTRY["RoughnessNode"] = WriteProcessor
    _NODE_TYPE_REGISTRY["MetallicNode"] = WriteProcessor
    _NODE_TYPE_REGISTRY["AONode"] = WriteProcessor
    _NODE_TYPE_REGISTRY["HeightNode"] = WriteProcessor


# Ensure the registry is populated with the standard node library.
auto_register_processors()


def register_processor(node_type_name: str, processor_cls: Type[ProcessorNode]) -> None:
    """
    Register a processor class under a node type name from the serialized graph.

    Args:
        node_type_name (str): The node type string as it appears in the
            serialized graph (e.g. "BevelNode").
        processor_cls (Type[ProcessorNode]): The processor class to instantiate
            for that node type.
    """
    _NODE_TYPE_REGISTRY[node_type_name] = processor_cls


class ProcessorGraph(object):
    """
    A headless graph of connected ProcessorNodes, constructed from a serialized
    Catena graph.

    Provides methods for evaluating nodes, querying the graph, and writing
    output data.
    """

    def __init__(self) -> None:
        auto_register_processors()
        self._nodes: dict[str, ProcessorNode] = {}
        self._node_types: dict[str, str] = {}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ProcessorGraph":
        """
        Construct a ProcessorGraph from a deserialized graph dict.

        Args:
            data (dict[str, Any]): The deserialized graph data containing
                "nodes" and "wires" keys.
        Returns:
            ProcessorGraph: The constructed headless graph.
        Raises:
            KeyError: If a node type is not registered in the processor registry.
        """
        graph = cls()

        _SKIP_TYPES = {"CatenaCommentBox"}

        for node_data in data["nodes"]:
            node_id = node_data["id"]
            node_type = node_data["type"]
            fields = node_data.get("fields", {})

            if node_type in _SKIP_TYPES:
                continue

            if node_type not in _NODE_TYPE_REGISTRY:
                continue

            processor_cls = _NODE_TYPE_REGISTRY[node_type]
            processor = processor_cls()

            for name, value in fields.items():
                if hasattr(processor, name):
                    setattr(processor, name, value)

            graph._nodes[node_id] = processor
            graph._node_types[node_id] = node_type

        for wire in data["wires"]:
            source_id = wire["source_node"]
            target_id = wire["target_node"]

            if source_id not in graph._nodes or target_id not in graph._nodes:
                continue

            source = graph._nodes[source_id]
            target = graph._nodes[target_id]
            source_name = wire["source_port"]
            target_name = wire["target_port"]
            target.connect(target_name, source, source_port=source_name)

        return graph

    @classmethod
    def from_json(cls, filepath: str | Path) -> "ProcessorGraph":
        """
        Construct a ProcessorGraph from a serialized JSON file.

        Args:
            filepath (str | Path): Path to the .cat JSON file.
        Returns:
            ProcessorGraph: The constructed headless graph.
        """
        path = Path(filepath)
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)

    def get_node(self, node_id: str) -> Optional[ProcessorNode]:
        """
        Retrieve a processor node by its graph ID.

        Args:
            node_id (str): The node's ID as it appears in the serialized graph.
        Returns:
            ProcessorNode | None: The processor node, or None if not found.
        """
        return self._nodes.get(node_id)

    def get_all_nodes_of_type(self, processor_cls: Type[T]) -> list[T]:
        """
        Return all processor nodes that are instances of the given class.

        Args:
            processor_cls (Type[T]): The processor class to filter by.
        Returns:
            list[T]: All matching processor nodes.
        """
        return [
            node for node in self._nodes.values() if isinstance(node, processor_cls)
        ]

    def get_nodes_by_type_name(self, node_type_name: str) -> list[ProcessorNode]:
        """
        Return all processor nodes registered under a given node type name.

        Args:
            node_type_name (str): The node type string as it appears in the
                serialized graph (e.g. "BevelNode").
        Returns:
            list[ProcessorNode]: All matching processor nodes.
        """
        return [
            self._nodes[node_id]
            for node_id, type_name in self._node_types.items()
            if type_name == node_type_name
        ]

    def evaluate_node(
        self, node_id: str
    ) -> numpy.ndarray | None | dict[str, numpy.ndarray | None]:
        """
        Evaluate a specific node by its graph ID.

        Args:
            node_id (str): The node's ID as it appears in the serialized graph.
        Returns:
            numpy.ndarray | dict[str, numpy.ndarray | None] | None: The evaluated
                output. Returns a plain ndarray for single-output nodes, a dict
                keyed by output port name for multi-output nodes (e.g. SplitNode),
                or None if the node is not found or produces no output.
        """
        node = self._nodes.get(node_id)
        if node is None:
            return None
        return node.evaluate()

    def evaluate_all(
        self,
    ) -> dict[str, numpy.ndarray | None | dict[str, numpy.ndarray | None]]:
        """
        Evaluate all nodes in the graph.

        Returns:
            dict[str, numpy.ndarray | None | dict[str, numpy.ndarray | None]]:
                A mapping of node ID to evaluated output for every node in the
                graph. Values are plain ndarrays for single-output nodes, dicts
                keyed by output port name for multi-output nodes, or None for
                nodes that produce no output.
        """
        return {node_id: node.evaluate() for node_id, node in self._nodes.items()}

    def write_all(self) -> dict[str, bool]:
        """
        Call write_image() on all nodes that support it (e.g. WriteNode
        subclasses), returning a map of node ID to success status.

        Returns:
            dict[str, bool]: A mapping of node ID to whether the write
                succeeded.
        """
        results: dict[str, bool] = {}
        for node_id, node in self._nodes.items():
            if hasattr(node, "write_image"):
                image = node.evaluate()
                results[node_id] = node.write_image(image)
        return results

    def node_ids(self) -> list[str]:
        """
        Return all node IDs present in this graph.

        Returns:
            list[str]: All node IDs.
        """
        return list(self._nodes.keys())

    def __len__(self) -> int:
        return len(self._nodes)

    def __repr__(self) -> str:
        return f"ProcessorGraph({len(self._nodes)} nodes)"
