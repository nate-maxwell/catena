from typing import Optional

import numpy
from PySide6TK.Nodes import PortType

from catena.nodes.convert import IMAGE_NODE_COLOR
from catena.nodes.data import PortDataType
from catena.nodes.node_gui import CatenaNode
from catena.nodes.node_processor import ProcessorNode


class FloatToIntProcessor(ProcessorNode):
    """A headless processor that floors a float image to integer-like steps."""

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        """
        Floor a float image to integer-like discrete steps by multiplying
        by 255, flooring, then dividing back to [0, 1].

        Args:
            inputs (dict[str, numpy.ndarray | None]): Expects key "Input"
                containing a float32 image with values in [0, 1].
        Returns:
            numpy.ndarray | None: A float32 image with values quantized to
                integer steps in [0, 1].
        """
        image = inputs.get("Input")
        if image is None:
            return None

        return (numpy.floor(image * 255.0) / 255.0).astype(numpy.float32)


class FloatToIntNode(CatenaNode):
    """A node that converts a float image to integer-quantized steps."""

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        self._processor = FloatToIntProcessor()
        super().__init__(title="Float to Int", width=120, body_height=20)

    def _build(self) -> None:
        self.port_in = self.add_port(PortType.INPUT, "Input", PortDataType.FLOAT)
        self.port_out = self.add_port(PortType.OUTPUT, "Output", PortDataType.VECTOR1)

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        return self._processor.process(inputs)
