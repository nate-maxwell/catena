from typing import Optional

import numpy
from PySide6TK.Nodes import PortType

from catena.nodes.node_gui import CatenaNode
from catena.nodes.image import IMAGE_NODE_COLOR
from catena.nodes.node_processor import ProcessorNode


class NormalizeProcessor(ProcessorNode):
    """A headless processor that remaps an image's value range to [0, 1]."""

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        """
        Remap an image's value range so its minimum becomes 0 and maximum becomes 1.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Expects key "Input"
                containing a float32 image.
        Returns:
            numpy.ndarray | None: The normalized float32 image with values
                in [0, 1], or a zero image if the input has no range.
        """
        image = inputs.get("Input")
        if image is None:
            return None

        minimum = image.min()
        maximum = image.max()

        range_value = maximum - minimum
        if range_value <= 1e-6:
            return numpy.zeros_like(image, dtype=numpy.float32)

        return ((image - minimum) / range_value).astype(numpy.float32)


class NormalizeNode(CatenaNode):
    """
    A node that remaps an input's value range so its minimum becomes 0 and
    maximum becomes 1.
    """

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        self._processor = NormalizeProcessor()
        super().__init__(title="Normalize")

    def _build(self) -> None:
        self.port_in = self.add_port(PortType.INPUT, "Input")
        self.port_out = self.add_port(PortType.OUTPUT, "Output")

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        return self._processor.process(inputs)
