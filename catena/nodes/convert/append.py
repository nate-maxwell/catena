from typing import Optional

import numpy
from PySide6TK.Nodes import PortType

from catena.nodes.node_gui import CatenaNode
from catena.nodes.convert import IMAGE_NODE_COLOR
from catena.nodes.data import PortDataType
from catena.nodes.node_processor import ProcessorNode


class AppendProcessor(ProcessorNode):
    """A headless processor that combines individual channel inputs into a vector4 modifier."""

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        """
        Combine Red, Green, Blue, and Alpha channel inputs into a BGRA modifier.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Evaluated images keyed
                by port name. Expects keys "Red", "Green", "Blue", "Alpha".
        Returns:
            numpy.ndarray | None: A float32 BGRA modifier of shape (H, W, 4).
        """
        red = inputs.get("Red")
        green = inputs.get("Green")
        blue = inputs.get("Blue")
        alpha = inputs.get("Alpha")

        height, width = 512, 512
        for channel in (red, green, blue, alpha):
            if channel is not None:
                height, width = channel.shape[:2]
                break

        def _to_single_channel(channel: Optional[numpy.ndarray]) -> numpy.ndarray:
            if channel is None:
                return numpy.zeros((height, width), dtype=numpy.float32)
            if channel.ndim == 3:
                return channel.mean(axis=2).astype(numpy.float32)
            return channel.astype(numpy.float32)

        r = _to_single_channel(red)
        g = _to_single_channel(green)
        b = _to_single_channel(blue)
        a = _to_single_channel(alpha)

        return numpy.stack([b, g, r, a], axis=-1).astype(numpy.float32)


class AppendNode(CatenaNode):
    """A node that combines individual channel inputs into a vector4 modifier."""

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        super().__init__(title="Append")
        self._processor = AppendProcessor()

    def _build(self) -> None:
        self.port_in_r = self.add_port(PortType.INPUT, "Red", PortDataType.VECTOR1)
        self.port_in_g = self.add_port(PortType.INPUT, "Green", PortDataType.VECTOR1)
        self.port_in_b = self.add_port(PortType.INPUT, "Blue", PortDataType.VECTOR1)
        self.port_in_a = self.add_port(PortType.INPUT, "Alpha", PortDataType.VECTOR1)
        self.port_out = self.add_port(PortType.OUTPUT, "Output", PortDataType.VECTOR4)

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        return self._processor.process(inputs)
