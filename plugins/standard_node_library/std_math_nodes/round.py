from typing import Optional

import numpy

from catena import api
from std_math_nodes.math_node import MathNode


class RoundNode(MathNode):
    """A node that rounds an input modifier to the nearest integer."""

    def __init__(self) -> None:
        super().__init__(title="Round")

    def _build(self) -> None:
        self.port_in = self.add_port(api.PortType.INPUT, "Input", api.PortDataType.VECTOR4)
        self.port_out = self.add_port(api.PortType.OUTPUT, "Output", api.PortDataType.VECTOR4)
        super()._build()

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        """
        Round an input modifier to the nearest whole number.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Expects key "Input"
                containing a float32 modifier.
        Returns:
            numpy.ndarray | None: The rounded float32 modifier.
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

        return numpy.rint(image).astype(numpy.float32)
