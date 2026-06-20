from typing import Optional

import numpy
from PySide6TK.Nodes import PortType

from catena.nodes.base import CatenaNode
from catena.nodes.convert import IMAGE_NODE_COLOR
from catena.nodes.data import PortDataType
from catena.nodes.processor import ProcessorNode


class SplitProcessor(ProcessorNode):
    """A headless processor that splits a vector4 image into individual channel outputs."""

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[dict[str, Optional[numpy.ndarray]]]:
        """
        Split a BGRA image into individual channel outputs.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Expects key "Input"
                containing a float32 BGRA image.
        Returns:
            dict[str, numpy.ndarray | None]: Keys "Red", "Green", "Blue",
                "Alpha", each a float32 (H, W, 3) grayscale image of that
                channel, or None if the input is None.
        """
        image = inputs.get("Input")

        if image is None:
            return {
                "Red": None,
                "Green": None,
                "Blue": None,
                "Alpha": None,
            }

        height, width = image.shape[:2]
        zeros = numpy.zeros((height, width, 1), dtype=numpy.float32)

        def _extract(channel_idx: int) -> numpy.ndarray:
            if image.ndim < 3 or image.shape[2] <= channel_idx:
                return numpy.repeat(zeros, 3, axis=2).astype(numpy.float32)
            channel = image[:, :, channel_idx : channel_idx + 1]
            return numpy.repeat(channel, 3, axis=2).astype(numpy.float32)

        return {
            "Red": _extract(2),
            "Green": _extract(1),
            "Blue": _extract(0),
            "Alpha": _extract(3),
        }


class SplitNode(CatenaNode):
    """A node that splits a vector4 (or smaller) image into individual channel outputs."""

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        self._processor = SplitProcessor()
        super().__init__(title="Split")

    def _build(self) -> None:
        self.port_in = self.add_port(PortType.INPUT, "Input", PortDataType.VECTOR4)
        self.port_out_r = self.add_port(PortType.OUTPUT, "Red", PortDataType.VECTOR1)
        self.port_out_g = self.add_port(PortType.OUTPUT, "Green", PortDataType.VECTOR1)
        self.port_out_b = self.add_port(PortType.OUTPUT, "Blue", PortDataType.VECTOR1)
        self.port_out_a = self.add_port(PortType.OUTPUT, "Alpha", PortDataType.VECTOR1)

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[dict[str, Optional[numpy.ndarray]]]:
        return self._processor.process(inputs)
