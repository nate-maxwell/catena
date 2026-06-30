from typing import Optional

import numpy

from catena import api
from std_graph_nodes import IMAGE_NODE_COLOR

_PORT_TYPES = [v for k, v in vars(api.PortDataType).items() if not k.startswith("_")]


class SwitchNode(api.CatenaNode):
    """A node that selects between two inputs using a switch value."""

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        super().__init__(title="Switch")

    def _build(self) -> None:
        self.port_in_a = self.add_port(
            api.PortType.INPUT, "A", api.PortDataType.VECTOR4
        )
        self.port_in_b = self.add_port(
            api.PortType.INPUT, "B", api.PortDataType.VECTOR4
        )
        self.port_out = self.add_port(
            api.PortType.OUTPUT, "Output", api.PortDataType.VECTOR4
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
        self.add_field(
            api.FieldDefinition(
                name="switch",
                label="Switch",
                field_type=api.FieldType.FLOAT,
                default=0.0,
                min_value=0.0,
                max_value=1.0,
            )
        )

        self.promote_field("switch")

    def _on_field_changed(self, node: "SwitchNode") -> None:
        data_type = self.get_field_value("data_type")
        for port in (self.port_in_a, self.port_in_b, self.port_out):
            port.data_type = data_type
            port.set_color(api.DATA_TYPE_COLORS[data_type])

        super()._on_field_changed(node)

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        """
        Select between A and B using the switch value.

        The selector defaults to the field value, but because it is a float
        field, it can also be promoted to an input port from the properties
        panel when you want to drive it from upstream nodes.
        """
        image_a = inputs.get("A")
        image_b = inputs.get("B")
        switch_value = float(self.get_field_value("switch"))

        if image_a is None and image_b is None:
            return None

        if switch_value < 0.5:
            return image_a if image_a is not None else image_b

        return image_b if image_b is not None else image_a

    def on_input_connection_changed(self, port: api.Port) -> None:
        self._invalidate_downstream()
        self._cached_value = None
        self._on_field_changed(self)
