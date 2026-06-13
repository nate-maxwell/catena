from typing import Optional

import cv2
import numpy
from PySide6TK.Nodes.node import PortType

from catena.core.nodes.base import CatenaNode
from catena.core.nodes.math import IMAGE_NODE_COLOR


class MultiplyNode(CatenaNode):
    """A node that multiplies two input images together."""

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        super().__init__(title="Multiply", width=180, body_height=60)

    def _build(self) -> None:
        self.port_in_a = self.add_port(PortType.INPUT, "A")
        self.port_in_b = self.add_port(PortType.INPUT, "B")
        self.port_out = self.add_port(PortType.OUTPUT, "Output")

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        image_a = inputs.get("A")
        image_b = inputs.get("B")

        if image_a is None or image_b is None:
            return None

        if image_a.shape != image_b.shape:
            height, width = image_a.shape[:2]
            image_b = cv2.resize(image_b, (width, height))

        factor = image_b.astype(numpy.float32) / 255.0
        result = image_a.astype(numpy.float32) * factor
        result = numpy.clip(result, 0, 255).astype(numpy.uint8)
        return result
