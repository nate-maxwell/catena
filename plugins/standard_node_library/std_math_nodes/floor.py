from typing import Optional

import numpy

from catena import api
from std_math_nodes import IMAGE_NODE_COLOR


class FloorNode(api.CatenaNode):
    """A node that applies a floor function to an input modifier."""

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        super().__init__(title="Floor")

    def _build(self) -> None:
        self.port_in = self.add_port(api.PortType.INPUT, "Input")
        self.port_out = self.add_port(api.PortType.OUTPUT, "Output")

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        image = inputs.get("Input")
        if image is None:
            return None

        return numpy.floor(image).astype(numpy.float32)
