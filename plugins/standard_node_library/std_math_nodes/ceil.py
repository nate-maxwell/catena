from typing import Optional

import numpy

from catena import api
from std_math_nodes.math_node import MathNode


class CeilNode(MathNode):
    """A node that applies a ceiling function to an input modifier."""

    def __init__(self) -> None:
        super().__init__(title="Ceil")

    def _build(self) -> None:
        self.port_in = self.add_port(api.PortType.INPUT, "Input", api.PortDataType.VECTOR4)
        self.port_out = self.add_port(api.PortType.OUTPUT, "Output", api.PortDataType.VECTOR4)
        super()._build()

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        """
        Apply a ceiling function to an input modifier, rounding each value up
        to the nearest integer.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Expects key "Input"
                containing a float32 modifier with values in [0, 1].
        Returns:
            numpy.ndarray | None: The ceiled float32 modifier.
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

        return numpy.ceil(image).astype(numpy.float32)
