from typing import Optional

import numpy
from PySide6TK.Nodes import PortType

from catena.nodes.convert import IMAGE_NODE_COLOR
from catena.nodes.data import PortDataType
from catena.nodes.node_gui import CatenaNode
from catena.nodes.node_processor import ProcessorNode


class IntToFloatProcessor(ProcessorNode):
    """A headless processor that converts an integer-quantized image to float."""

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


class IntToFloatNode(CatenaNode):
    """A node that converts an integer-quantized image to a float image."""

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        self._processor = IntToFloatProcessor()
        super().__init__(title="Int to Float", width=120, body_height=20)

    def _build(self) -> None:
        self.port_in = self.add_port(PortType.INPUT, "Input", PortDataType.INT)
        self.port_out = self.add_port(PortType.OUTPUT, "Output", PortDataType.FLOAT)

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        return self._processor.process(inputs)
