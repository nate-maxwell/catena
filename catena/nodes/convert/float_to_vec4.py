from typing import Optional

import numpy
from PySide6TK.Nodes import PortType

from catena.nodes.convert import IMAGE_NODE_COLOR
from catena.nodes.data import PortDataType
from catena.nodes.node_gui import CatenaNode
from catena.nodes.node_processor import ProcessorNode


class FloatToVec4Processor(ProcessorNode):
    """A headless processor that converts a float image to a vector4 image."""

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        """
        Pass a float image through as a vector4 image.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Expects key "Input"
                containing a float32 image with values in [0, 1].
        Returns:
            numpy.ndarray | None: A float32 vector4 image with values in [0, 1].
        """
        image = inputs.get("Input")
        if image is None:
            return None

        return image.astype(numpy.float32)


class FloatToVec4Node(CatenaNode):
    """A node that converts a float image to a vector4 image."""

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        self._processor = FloatToVec4Processor()
        super().__init__(title="Float to Vec4", width=130, body_height=20)

    def _build(self) -> None:
        self.port_in = self.add_port(PortType.INPUT, "Input", PortDataType.FLOAT)
        self.port_out = self.add_port(PortType.OUTPUT, "Output", PortDataType.VECTOR4)

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        return self._processor.process(inputs)
