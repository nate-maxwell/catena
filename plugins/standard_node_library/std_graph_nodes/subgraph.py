import json
from pathlib import Path
from typing import Optional

import broker
import numpy
from PySide6TK import QtCore
from PySide6TK import QtWidgets

from catena import api
from catena import appdata
from catena import namespace
from catena import session
from catena.nodes.graph import GuiGraphView
from catena.nodes.node import CatenaNode
from catena.nodes import serialize as graph_serialize
from std_graph_nodes.input import GraphInputNode
from std_graph_nodes.input import default_field_for_data_type
from std_graph_nodes.input import numeric_field_limits_for_data_type
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
        self._dynamic_input_names: list[str] = []
        self._cached_filepath: str = ""
        self._graph_name: str = "Subgraph"
        self._cached_graph_view: GuiGraphView | None = None
        self._cached_graph_view_path: str = ""
        self._cached_graph_view_mtime: int | None = None
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

    def _resolve_filepath(self, filepath: str | Path | None = None) -> Path | None:
        """
        Resolve a subgraph filepath against common relative locations.

        Absolute paths are used as-is. Relative paths are checked against the
        current working directory, the current project file directory, and the
        built-in plugins directory.
        """
        if filepath is None:
            filepath = self.get_field_value("filepath")

        if not filepath:
            return None

        path = Path(filepath)
        if path.is_absolute():
            return path if path.exists() else None

        candidates = [
            Path.cwd() / path,
        ]

        project_file = session.SessionData().project_file
        if project_file:
            candidates.append(project_file.parent / path)

        candidates.append(appdata.BUILT_IN_PLUGINS_PATH / path)

        for candidate in candidates:
            if candidate.exists():
                return candidate

        return None

    def open_subgraph(self) -> None:
        """
        Open the subgraph referenced by this node's filepath.
        """
        path = self._resolve_filepath(self._cached_filepath)
        if path is None:
            return

        broker.emit(namespace.GRAPH_OPEN_SUBGRAPH, file_path=path)

    def evaluate(
        self,
    ) -> Optional[numpy.ndarray] | dict[str, Optional[numpy.ndarray]]:
        """
        Evaluate the subgraph and cache the outer result until the inner graph
        or one of this node's exposed values changes.
        """
        self._invalidate_cached_result_if_source_changed()
        return super().evaluate()

    def mouseReleaseEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent) -> None:
        # RMB on subgraph should open the subgraph
        if event.button() == QtCore.Qt.MouseButton.RightButton:
            self.open_subgraph()
            event.accept()
            return

        super().mouseReleaseEvent(event)

    def _on_field_changed(self, node: "SubgraphNode") -> None:
        filepath = self.get_field_value("filepath")
        if filepath != self._cached_filepath:
            self._cached_filepath = filepath
            self._cached_graph_view = None
            self._cached_graph_view_path = ""
            self._cached_graph_view_mtime = None
            self._rebuild_ports()
        super()._on_field_changed(node)

    def _invalidate_cached_result_if_source_changed(self) -> None:
        """Invalidate the cached outer result when the subgraph file changes."""
        path = self._resolve_filepath()
        if path is None:
            self._cached_value = None
            return

        current_mtime = path.stat().st_mtime_ns
        if (
            path.as_posix() != self._cached_graph_view_path
            or current_mtime != self._cached_graph_view_mtime
        ):
            self._cached_value = None

    def _load_interface(
        self,
    ) -> tuple[
        list[tuple[str, str, object]],
        list[tuple[str, str]],
    ]:
        """
        Read the subgraph file and return the names, data types, and default
        values of all GraphInput nodes, plus the names and data types of all
        GraphOutput nodes, in the order they appear.

        Returns:
            tuple[list[tuple[str, str, object]], list[tuple[str, str]]]: Input
                (name, data_type, default_value) tuples and output
                (name, data_type) tuples.
        """
        if not self._cached_filepath:
            return [], []

        path = self._resolve_filepath(self._cached_filepath)
        if path is None:
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
            default_value = fields.get("default_value")

            if node_type == "GraphInputNode":
                input_ports.append((name, data_type, default_value))
            elif node_type == "GraphOutputNode":
                output_ports.append((name, data_type))

        return input_ports, output_ports

    def _load_graph_view(self) -> GuiGraphView | None:
        """
        Return a cached in-memory graph view for the current subgraph file.
        """
        path = self._resolve_filepath()
        if path is None:
            return None

        current_mtime = path.stat().st_mtime_ns
        if (
            self._cached_graph_view is not None
            and self._cached_graph_view_path == path.as_posix()
            and self._cached_graph_view_mtime == current_mtime
        ):
            return self._cached_graph_view

        view = GuiGraphView()
        graph_serialize.load(view, path)
        self._cached_graph_view = view
        self._cached_graph_view_path = path.as_posix()
        self._cached_graph_view_mtime = current_mtime

        def invalidate_cached_result() -> None:
            # Stupid python gets annoyed when using 'self' in a lambda...
            self._cached_value = None

        view.graph_scene.changed.connect(invalidate_cached_result)

        return view

    def _clear_dynamic_interface(self) -> None:
        """Remove the currently generated ports and backing fields."""
        for name in list(self._dynamic_input_names):
            self.demote_field(name)
            self._fields.pop(name, None)
            self._field_values.pop(name, None)

        for port in list(self._output_ports.values()):
            self.remove_port(port)

        self._dynamic_input_names.clear()
        self._input_ports.clear()
        self._output_ports.clear()

    def _rebuild_ports(self) -> None:
        """
        Remove all existing dynamic ports and rebuild them based on the
        GraphInputNode and GraphOutputNode nodes in the subgraph file.
        """
        self._clear_dynamic_interface()

        input_ports, output_ports = self._load_interface()

        self.title = self._graph_name
        self.update()

        for name, data_type, default_value in input_ports:
            default_field_type, fallback_default = default_field_for_data_type(
                data_type
            )
            min_value, max_value = numeric_field_limits_for_data_type(data_type)
            if default_value is None:
                default_value = fallback_default
            definition = api.FieldDefinition(
                name=name,
                label=name,
                field_type=default_field_type,
                default=default_value,
                min_value=min_value,
                max_value=max_value,
            )
            self.add_field(definition)

            port = self.add_port(api.PortType.INPUT, name, data_type)
            port.set_color(api.DATA_TYPE_COLORS[data_type])
            self._promoted_fields[name] = port
            self._dynamic_input_names.append(name)
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
            if not isinstance(node, GraphInputNode):
                continue

            input_name = node.get_field_value("name")
            input_data_type = node.get_field_value("data_type")
            outer_value = inputs.get(input_name)
            if outer_value is None:
                outer_value = self._field_values.get(input_name)

            node._invalidate_downstream()
            node._cached_value = api.modifier_value_for_data_type(
                input_data_type, outer_value
            )

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
