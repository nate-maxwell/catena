from typing import Optional

import numpy
from PySide6TK.Nodes import PortType

from catena.nodes.node_gui import CatenaNode
from catena.nodes.node_processor import ProcessorNode
from catena.nodes.math import IMAGE_NODE_COLOR


class FloorProcessor(ProcessorNode):
    """A headless processor that applies a floor function to an modifier."""

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        """
        Apply a floor function to an input modifier, rounding each value down
        to the nearest integer.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Expects key "Input"
                containing a float32 modifier with values in [0, 1].
        Returns:
            numpy.ndarray | None: The floored float32 modifier.
        """
        image = inputs.get("Input")
        if image is None:
            return None

        return numpy.floor(image).astype(numpy.float32)


class FloorNode(CatenaNode):
    """A node that applies a floor function to an input modifier."""

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        self._processor = FloorProcessor()
        super().__init__(title="Floor")

    def _build(self) -> None:
        self.port_in = self.add_port(PortType.INPUT, "Input")
        self.port_out = self.add_port(PortType.OUTPUT, "Output")

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        return self._processor.process(inputs)
