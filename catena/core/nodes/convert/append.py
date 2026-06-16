from typing import Optional

import numpy
from PySide6TK.Nodes.node import PortType

from catena.core.nodes.base import CatenaNode
from catena.core.nodes.data import PortDataType
from catena.core.nodes.convert import IMAGE_NODE_COLOR


class AppendNode(CatenaNode):
    """A node that combines individual channel inputs into a vector4 image."""

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        super().__init__(title="Append")

    def _build(self) -> None:
        self.port_in_r = self.add_port(PortType.INPUT, "Red", PortDataType.VECTOR1)
        self.port_in_g = self.add_port(PortType.INPUT, "Green", PortDataType.VECTOR1)
        self.port_in_b = self.add_port(PortType.INPUT, "Blue", PortDataType.VECTOR1)
        self.port_in_a = self.add_port(PortType.INPUT, "Alpha", PortDataType.VECTOR1)
        self.port_out = self.add_port(PortType.OUTPUT, "Output", PortDataType.VECTOR4)

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
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

        result = numpy.stack([b, g, r, a], axis=-1).astype(numpy.float32)
        return result
