from typing import Optional

import numpy

from catena import api
from std_convert_nodes import IMAGE_NODE_COLOR


class IntToFloatNode(api.CatenaNode):
    """A node that converts an integer-quantized image to a float image."""

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        super().__init__(title="Int to Float", width=120, body_height=20)

    def _build(self) -> None:
        self.port_in = self.add_port(api.PortType.INPUT, "Input", api.PortDataType.INT)
        self.port_out = self.add_port(
            api.PortType.OUTPUT, "Output", api.PortDataType.FLOAT
        )

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        """
        Pass an integer-quantized image through as a float, normalizing
        to [0, 1] if needed.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Expects key "Input"
                containing a float32 image with values in [0, 1].
        Returns:
            numpy.ndarray | None: A float32 image with values in [0, 1].
        """
        image = inputs.get("Input")
        if image is None:
            return None

        return image.astype(numpy.float32)
