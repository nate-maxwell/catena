from typing import Optional

import numpy

from catena import api
from std_convert_nodes import IMAGE_NODE_COLOR


class AppendNode(api.CatenaNode):
    """A node that combines individual channel inputs into a vector4 modifier."""

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        super().__init__(title="Append")

    def _build(self) -> None:
        self.port_in_r = self.add_port(
            api.PortType.INPUT, "Red", api.PortDataType.VECTOR1
        )
        self.port_in_g = self.add_port(
            api.PortType.INPUT, "Green", api.PortDataType.VECTOR1
        )
        self.port_in_b = self.add_port(
            api.PortType.INPUT, "Blue", api.PortDataType.VECTOR1
        )
        self.port_in_a = self.add_port(
            api.PortType.INPUT, "Alpha", api.PortDataType.VECTOR1
        )
        self.port_out = self.add_port(
            api.PortType.OUTPUT, "Output", api.PortDataType.VECTOR4
        )

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

        height, width = api.get_texture_resolution()
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
