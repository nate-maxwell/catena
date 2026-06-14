from typing import Optional

import numpy
from PySide6TK.Nodes.node import PortType

from catena.core.nodes.base import CatenaNode
from catena.core.nodes.image import IMAGE_NODE_COLOR


class NormalizeNode(CatenaNode):
    """
    A node that remaps an input's value range so its minimum becomes 0 and
    maximum becomes 1.
    """

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        super().__init__(title="Normalize")

    def _build(self) -> None:
        self.port_in = self.add_port(PortType.INPUT, "Input")
        self.port_out = self.add_port(PortType.OUTPUT, "Output")

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        image = inputs.get("Input")
        if image is None:
            return None

        minimum = image.min()
        maximum = image.max()

        range_value = maximum - minimum
        if range_value <= 1e-6:
            return numpy.zeros_like(image, dtype=numpy.float32)

        result = (image - minimum) / range_value
        return result.astype(numpy.float32)
