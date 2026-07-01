from typing import Optional

import broker
import numpy

from catena import api
from catena import namespace
from std_graph_nodes import IMAGE_NODE_COLOR

_PORT_TYPES = [v for k, v in vars(api.PortDataType).items() if not k.startswith("_")]


def default_field_for_data_type(data_type: str) -> tuple[str, object]:
    """Generates a default value and type pair for each data type."""
    if data_type in (api.PortDataType.FLOAT, api.PortDataType.VECTOR1):
        return api.FieldType.FLOAT, 0.0
    if data_type == api.PortDataType.INT:
        return api.FieldType.INT, 0
    if data_type == api.PortDataType.BOOL:
        return api.FieldType.BOOL, False
    if data_type == api.PortDataType.VECTOR2:
        return api.FieldType.VEC2, (0.0, 0.0)
    if data_type == api.PortDataType.VECTOR3:
        return api.FieldType.VEC3, (0.0, 0.0, 0.0)
    return api.FieldType.COLOR, (255, 255, 255, 255)


def numeric_field_limits_for_data_type(
    data_type: str,
) -> tuple[object | None, object | None]:
    """Sets the upper bounds of the input values to 999999.0 for numeric types."""
    if data_type in (api.PortDataType.FLOAT, api.PortDataType.VECTOR1):
        return 0.0, 999999.0
    if data_type == api.PortDataType.INT:
        return 0, 999999
    return None, None


class GraphInputNode(api.CatenaNode):
    """
    A node that defines a named input port for a subgraph.
    Appears as an input port on the SubgraphNode in the outer graph.
    """

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        super().__init__(title="Graph Input", width=140, body_height=20)

    def _build(self) -> None:
        self.port_out = self.add_port(
            api.PortType.OUTPUT, "Output", api.PortDataType.VECTOR4
        )

        self.add_field(
            api.FieldDefinition(
                name="name",
                label="Name",
                field_type=api.FieldType.STR,
                default="Input",
            )
        )
        self.add_field(
            api.FieldDefinition(
                name="data_type",
                label="Type",
                field_type=api.FieldType.CHOICE,
                default=api.PortDataType.VECTOR4,
                options=_PORT_TYPES,
            )
        )
        default_field_type, default_value = default_field_for_data_type(
            api.PortDataType.VECTOR4
        )
        self.add_field(
            api.FieldDefinition(
                name="default_value",
                label="Default",
                field_type=default_field_type,
                default=default_value,
            )
        )
        self._sync_port_from_fields()

    def _sync_port_from_fields(self) -> None:
        name = self.get_field_value("name")
        data_type = self.get_field_value("data_type")

        self.port_out.name = name
        self.port_out.data_type = data_type
        self.port_out.set_color(api.DATA_TYPE_COLORS[data_type])

    def _on_field_changed(self, node: "GraphInputNode") -> None:
        self._sync_port_from_fields()
        data_type = self.get_field_value("data_type")
        default_field_type, default_value = default_field_for_data_type(data_type)
        for wire in list(self.port_out.wires):
            wire.refresh_color()
            wire.update_path()

        definition = self._fields.get("default_value")
        if definition is not None and definition.field_type != default_field_type:
            definition.field_type = default_field_type
            definition.default = default_value
            definition.min_value, definition.max_value = (
                numeric_field_limits_for_data_type(data_type)
            )
            self._field_values["default_value"] = default_value
            self.update()
            broker.emit(namespace.NODE_SELECTED, node=self)

        super()._on_field_changed(node)

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        """
        Emit the current default value as a modifier so downstream promoted
        fields can consume it.
        """
        data_type = self.get_field_value("data_type")
        value = self.get_field_value("default_value")

        if data_type == api.PortDataType.BOOL:
            return None

        if data_type in (api.PortDataType.FLOAT, api.PortDataType.VECTOR1):
            scalar = float(value)
            return numpy.full((1, 1, 1), scalar, dtype=numpy.float32)

        if data_type == api.PortDataType.INT:
            scalar = float(value)
            return numpy.full((1, 1, 1), scalar, dtype=numpy.float32)

        if data_type == api.PortDataType.VECTOR2:
            x, y = value
            return numpy.array([[[x, y, 0.0, 1.0]]], dtype=numpy.float32)

        if data_type == api.PortDataType.VECTOR3:
            x, y, z = value
            return numpy.array([[[x, y, z, 1.0]]], dtype=numpy.float32)

        r, g, b, a = value
        return numpy.array([[[r, g, b, a]]], dtype=numpy.float32) / 255.0
