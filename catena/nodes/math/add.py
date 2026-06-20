from typing import Optional

import cv2
import numpy
from PySide6TK.Nodes import PortType

from catena.nodes.node_gui import CatenaNode
from catena.nodes.math import IMAGE_NODE_COLOR
from catena.nodes.node_processor import ProcessorNode


class AddProcessor(ProcessorNode):
    """A headless processor that adds two input images together."""

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        """
        Add two input images together.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Expects keys "A" and "B",
                each containing a float32 image. Values may exceed [0, 1] and
                should be clamped downstream if needed.
        Returns:
            numpy.ndarray | None: The summed float32 image, or whichever
                input is non-None if only one is provided.
        """
        image_a = inputs.get("A")
        image_b = inputs.get("B")

        if image_a is None and image_b is None:
            return None
        if image_a is None:
            return image_b
        if image_b is None:
            return image_a

        if image_a.shape != image_b.shape:
            height, width = image_a.shape[:2]
            image_b = cv2.resize(image_b, (width, height))

        return (image_a + image_b).astype(numpy.float32)


class AddNode(CatenaNode):
    """A node that adds two input images together."""

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        self._processor = AddProcessor()
        super().__init__(title="Add")

    def _build(self) -> None:
        self.port_in_a = self.add_port(PortType.INPUT, "A")
        self.port_in_b = self.add_port(PortType.INPUT, "B")
        self.port_out = self.add_port(PortType.OUTPUT, "Output")

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        return self._processor.process(inputs)
