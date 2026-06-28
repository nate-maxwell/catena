from typing import Optional

import numpy

from catena import api
from std_modifier_nodes import IMAGE_NODE_COLOR


class NormalizeNode(api.CatenaNode):
    """
    A node that remaps an input's value range so its minimum becomes 0 and
    maximum becomes 1.
    """

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:

        super().__init__(title="Normalize")

    def _build(self) -> None:
        self.port_in = self.add_port(api.PortType.INPUT, "Input")
        self.port_out = self.add_port(api.PortType.OUTPUT, "Output")

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        """
        Remap n modifier's value range so its minimum becomes 0 and maximum becomes 1.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Expects key "Input"
                containing a float32 modifier.
        Returns:
            numpy.ndarray | None: The normalized float32 modifier with values
                in [0, 1], or a zero modifier if the input has no range.
        """
        image = inputs.get("Input")
        if image is None:
            return None

        result = image.astype(numpy.float32)
        minimum = float(result.min())
        maximum = float(result.max())

        range_value = maximum - minimum
        if range_value <= 1e-6:
            return numpy.zeros_like(result, dtype=numpy.float32)

        return ((result - minimum) / range_value).astype(numpy.float32)
