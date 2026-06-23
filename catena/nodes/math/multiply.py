from typing import Optional

import cv2
import numpy
from PySide6TK.Nodes import PortType

from catena.nodes.node_gui import CatenaNode
from catena.nodes.math import IMAGE_NODE_COLOR
from catena.nodes.node_processor import ProcessorNode


class MultiplyProcessor(ProcessorNode):
    """A headless processor that multiplies two input images together."""

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


class MultiplyNode(CatenaNode):
    """A node that multiplies two input images together."""

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        self._processor = MultiplyProcessor()
        super().__init__(title="Multiply")

    def _build(self) -> None:
        self.port_in_a = self.add_port(PortType.INPUT, "A")
        self.port_in_b = self.add_port(PortType.INPUT, "B")
        self.port_out = self.add_port(PortType.OUTPUT, "Output")

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        return self._processor.process(inputs)
