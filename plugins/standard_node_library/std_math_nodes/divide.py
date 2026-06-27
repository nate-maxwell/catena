from typing import Optional

import cv2
import numpy

from catena import api
from std_math_nodes import IMAGE_NODE_COLOR


class DivideNode(api.CatenaNode):
    """A node that divides one input modifier by another."""

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        super().__init__(title="Divide")

    def _build(self) -> None:
        self.port_in_a = self.add_port(api.PortType.INPUT, "A")
        self.port_in_b = self.add_port(api.PortType.INPUT, "B")
        self.port_out = self.add_port(api.PortType.OUTPUT, "Output")

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        """
        Divide modifier A by modifier B per-pixel.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Expects keys "A" and "B",
                each containing a float32 modifier. Both must be connected.
        Returns:
            numpy.ndarray | None: The divided float32 modifier. Values may
                exceed [0, 1] and should be clamped downstream if needed.
                Returns None if either input is missing.
        """
        image_a = inputs.get("A")
        image_b = inputs.get("B")

        if image_a is None or image_b is None:
            return None

        if image_a.shape != image_b.shape:
            height, width = image_a.shape[:2]
            image_b = cv2.resize(image_b, (width, height))

        a = image_a.astype(numpy.float32)
        b = numpy.where(image_b == 0, 1e-6, image_b.astype(numpy.float32))

        return (a / b).astype(numpy.float32)
