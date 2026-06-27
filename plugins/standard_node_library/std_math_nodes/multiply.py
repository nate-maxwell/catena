from typing import Optional

import cv2
import numpy

from catena import api
from std_math_nodes import IMAGE_NODE_COLOR


class MultiplyNode(api.CatenaNode):
    """A node that multiplies two input images together."""

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        super().__init__(title="Multiply")

    def _build(self) -> None:
        self.port_in_a = self.add_port(api.PortType.INPUT, "A")
        self.port_in_b = self.add_port(api.PortType.INPUT, "B")
        self.port_out = self.add_port(api.PortType.OUTPUT, "Output")

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        """
        Multiply two input images together per-pixel.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Expects keys "A" and "B",
                each containing a float32 modifier. Both must be connected.
        Returns:
            numpy.ndarray | None: The multiplied float32 modifier, or None if
                either input is missing.
        """
        image_a = inputs.get("A")
        image_b = inputs.get("B")

        if image_a is None or image_b is None:
            return None

        if image_a.shape != image_b.shape:
            height, width = image_a.shape[:2]
            image_b = cv2.resize(image_b, (width, height))

        return (image_a * image_b).astype(numpy.float32)
