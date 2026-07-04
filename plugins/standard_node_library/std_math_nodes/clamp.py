from typing import Optional

import numpy

from catena import api
from std_math_nodes import IMAGE_NODE_COLOR

_PORT_TYPES = [v for k, v in vars(api.PortDataType).items() if not k.startswith("_")]


class ClampNode(api.CatenaNode):
    """A node that clamps an input modifier to a configured range."""

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        super().__init__(title="Clamp")

    def _build(self) -> None:
        self.port_in = self.add_port(
            api.PortType.INPUT, "Input", api.PortDataType.VECTOR4
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
                name="minimum",
                label="Min",
                field_type=api.FieldType.FLOAT,
                default=0.0,
            )
        )
        self.add_field(
            api.FieldDefinition(
                name="maximum",
                label="Max",
                field_type=api.FieldType.FLOAT,
                default=1.0,
            )
        )

    def _on_field_changed(self, node: "ClampNode") -> None:
        data_type = self.get_field_value("data_type")
        for port in (self.port_in, self.port_out):
            port.data_type = data_type
            port.set_color(api.DATA_TYPE_COLORS[data_type])

        super()._on_field_changed(node)

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        """
        Clamp an input modifier to the configured range.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Expects key "Input"
                containing a numeric modifier.
        Returns:
            numpy.ndarray | None: The clamped float32 modifier, or None if the
                input is missing.
        """
        image = inputs.get("Input")
        if image is None:
            return None

        data_type = self.get_field_value("data_type")
        if data_type in (
            api.PortDataType.FLOAT,
            api.PortDataType.INT,
            api.PortDataType.VECTOR1,
        ) and image.ndim == 3:
            image = image.mean(axis=2, keepdims=True)

        minimum = float(self.get_field_value("minimum"))
        maximum = float(self.get_field_value("maximum"))
        lower = min(minimum, maximum)
        upper = max(minimum, maximum)

        return numpy.clip(image.astype(numpy.float32), lower, upper).astype(
            numpy.float32
        )
