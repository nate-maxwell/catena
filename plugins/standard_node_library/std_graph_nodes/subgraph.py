import json
from pathlib import Path
from typing import Optional

import broker
import numpy
from PySide6TK import QtWidgets

from catena import api
from catena import namespace
from catena.nodes.graph import GuiGraphView
from catena.nodes.node import CatenaNode
from catena.nodes import serialize as graph_serialize
from std_graph_nodes.input import GraphInputNode
from std_graph_nodes.output import GraphOutputNode
from std_graph_nodes import IMAGE_NODE_COLOR


class SubgraphNode(api.CatenaNode):
    """
    A node that loads a subgraph from a .cg file and dynamically builds
    input and output ports based on the GraphInputNode and GraphOutputNode
    nodes found within it.
    """

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        self._input_ports: dict[str, object] = {}
        self._output_ports: dict[str, object] = {}
        self._cached_filepath: str = ""
        self._graph_name: str = "Subgraph"
        self._cached_graph_view: GuiGraphView | None = None
        self._cached_graph_view_path: str = ""
        super().__init__(title="Subgraph")

    def _build(self) -> None:
        self.add_field(
            api.FieldDefinition(
                name="filepath",
                label="Filepath",
                field_type=api.FieldType.STR,
                default="",
            )
        )

    def open_subgraph(self) -> None:
        """
        Open the subgraph referenced by this node's filepath.
        """
        filepath = self._cached_filepath or self.get_field_value("filepath")
        if not filepath:
            return

        broker.emit(namespace.GRAPH_OPEN_SUBGRAPH, file_path=Path(filepath))

    def mouseDoubleClickEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent) -> None:
        self.open_subgraph()
        broker.emit(namespace.NODE_SELECTED, node=self)
        event.accept()

    def _on_field_changed(self, node: "SubgraphNode") -> None:
        filepath = self.get_field_value("filepath")
        if filepath != self._cached_filepath:
            self._cached_filepath = filepath
            self._cached_graph_view = None
            self._cached_graph_view_path = ""
            self._rebuild_ports()
        super()._on_field_changed(node)

    def _load_interface(self) -> tuple[list[tuple[str, str]], list[tuple[str, str]]]:
        """
        Read the subgraph file and return the names and data types of all
        GraphInput and GraphOutput nodes, in the order they appear.

        Returns:
            tuple[list[tuple[str, str]], list[tuple[str, str]]]: Input
                (name, data_type) pairs and output (name, data_type) pairs.
        """
        if not self._cached_filepath:
            return [], []

        path = Path(self._cached_filepath)
        if not path.exists():
            return [], []

        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        self._graph_name = path.stem.replace("_", " ").title()

        input_ports = []
        output_ports = []

        for node_data in data["nodes"]:
            node_type = node_data.get("type", "")
            fields = node_data.get("fields", {})
            name = fields.get("name", "")
            data_type = fields.get("data_type", api.PortDataType.VECTOR4)

            if node_type == "GraphInputNode":
                input_ports.append((name, data_type))
            elif node_type == "GraphOutputNode":
                output_ports.append((name, data_type))

        return input_ports, output_ports

    def _load_graph_view(self) -> GuiGraphView | None:
        """
        Return a cached in-memory graph view for the current subgraph file.
        """
        filepath = self.get_field_value("filepath")
        if not filepath:
            return None

        if (
            self._cached_graph_view is not None
            and self._cached_graph_view_path == filepath
        ):
            return self._cached_graph_view

        path = Path(filepath)
        if not path.exists():
            return None

        view = GuiGraphView()
        graph_serialize.load(view, path)
        self._cached_graph_view = view
        self._cached_graph_view_path = filepath
        return view

    def _rebuild_ports(self) -> None:
        """
        Remove all existing dynamic ports and rebuild them based on the
        GraphInputNode and GraphOutputNode nodes in the subgraph file.
        """
        for port in list(self._input_ports.values()):
            self.remove_port(port)
        for port in list(self._output_ports.values()):
            self.remove_port(port)

        self._input_ports.clear()
        self._output_ports.clear()

        input_ports, output_ports = self._load_interface()
        self.title = self._graph_name
        self.update()

        for name, data_type in input_ports:
            port = self.add_port(api.PortType.INPUT, name, data_type)
            port.set_color(api.DATA_TYPE_COLORS[data_type])
            self._input_ports[name] = port

        for name, data_type in output_ports:
            port = self.add_port(api.PortType.OUTPUT, name, data_type)
            port.set_color(api.DATA_TYPE_COLORS[data_type])
            self._output_ports[name] = port

        self.update()

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray] | dict[str, Optional[numpy.ndarray]]:
        """
        Evaluate the loaded subgraph and return its output value(s).

        The subgraph file is deserialized into an in-memory graph, GraphInput
        nodes are seeded from the outer node inputs, and the upstream node
        feeding each GraphOutput node is evaluated.
        """
        view = self._load_graph_view()
        if view is None:
            return None

        for node in view._node_refs:
            if isinstance(node, CatenaNode):
                node._cached_value = None

        for node in view._node_refs:
            if not isinstance(node, GraphInputNode):
                continue

            input_name = node.get_field_value("name")
            if input_name in inputs:
                node._cached_value = inputs[input_name]

        output_values: dict[str, Optional[numpy.ndarray]] = {}

        for node in view._node_refs:
            if not isinstance(node, GraphOutputNode):
                continue

            output_name = node.get_field_value("name")
            source_value: Optional[numpy.ndarray] = None

            if node.port_in.wires:
                source_port = node.port_in.wires[0].source
                source_node = source_port.parentItem()
                if isinstance(source_node, CatenaNode):
                    evaluated = source_node.evaluate()
                    if isinstance(evaluated, dict):
                        source_value = evaluated.get(source_port.name)
                    else:
                        source_value = evaluated

            output_values[output_name] = source_value

        if not output_values:
            return None

        if len(output_values) == 1:
            return next(iter(output_values.values()))

        return output_values
