from typing import Optional

import numpy
from PySide6TK.Nodes import PortType

from catena.nodes.node_gui import CatenaNode
from catena.nodes.modifier import IMAGE_NODE_COLOR
from catena.nodes.node_processor import ProcessorNode


class InvertProcessor(ProcessorNode):
    """A headless processor that inverts the colors of an modifier."""

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        """
        Invert the colors of an input modifier.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Expects key "Input"
                containing a float32 modifier with values in [0, 1].
        Returns:
            numpy.ndarray | None: The inverted float32 modifier.
        """
        image = inputs.get("Input")
        if image is None:
            return None

        return (1.0 - image).astype(numpy.float32)


class InvertNode(CatenaNode):
    """A node that inverts the colors of an input modifier."""

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        self._processor = InvertProcessor()
        super().__init__(title="Invert")

    def _build(self) -> None:
        self.port_in = self.add_port(PortType.INPUT, "Input")
        self.port_out = self.add_port(PortType.OUTPUT, "Output")

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        return self._processor.process(inputs)
