import json
from pathlib import Path

import broker
from PySide6TK import QtWidgets

from catena import api
from catena import namespace
from std_subgraph_nodes import IMAGE_NODE_COLOR


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
