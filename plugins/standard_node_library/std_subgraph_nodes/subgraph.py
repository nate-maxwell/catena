import json
from pathlib import Path
from typing import Optional

import broker
import numpy
from PySide6TK import QtWidgets

from catena import api
from catena import namespace
from catena.nodes.subgraph import IMAGE_NODE_COLOR
from catena.nodes.subgraph.input import GraphInputProcessor
from catena.nodes.subgraph.output import GraphOutputProcessor
from catena.nodes.graph_processor import ProcessorGraph


class SubgraphNode(api.CatenaNode):
    """
    A node that loads and evaluates a subgraph from a .cg file.
    Input and output ports are created dynamically based on the
    GraphInputNode and GraphOutputNode nodes found in the subgraph.
    """

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        self._input_ports: dict[str, object] = {}
        self._output_ports: dict[str, object] = {}
        self._cached_graph: Optional[ProcessorGraph] = None
        self._cached_filepath: str = ""
        self._graph_name: str = "Subgraph"
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

    def mouseDoubleClickEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent) -> None:
        filepath = self.get_field_value("filepath")
        if filepath:
            broker.emit(namespace.GRAPH_OPEN_SUBGRAPH, file_path=Path(filepath))
        super().mouseDoubleClickEvent(event)

    def _on_field_changed(self, node: "SubgraphNode") -> None:
        filepath = self.get_field_value("filepath")
        if filepath != self._cached_filepath:
            self._cached_filepath = filepath
            self._cached_graph = None
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
        filepath = self._cached_filepath
        if not filepath:
            return [], []

        path = Path(filepath)
        if not path.exists():
            return [], []

        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        self._graph_name = path.stem.title()

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
        filepath = self.get_field_value("filepath")

        if self._cached_graph is None and filepath:
            path = Path(filepath)
            if path.exists():
                self._cached_graph = ProcessorGraph.from_json(path)

        if self._cached_graph is None:
            return None

        input_processors = self._cached_graph.get_all_nodes_of_type(GraphInputProcessor)
        for processor in input_processors:
            processor.inject(inputs.get(processor.name))
            processor._cached_value = None

        output_processors = self._cached_graph.get_all_nodes_of_type(
            GraphOutputProcessor
        )

        if not output_processors:
            return None

        for processor in self._cached_graph._nodes.values():
            processor._cached_value = None

        if len(output_processors) == 1:
            return output_processors[0].evaluate()

        return {processor.name: processor.evaluate() for processor in output_processors}
