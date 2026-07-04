from typing import Optional

import cv2
import numpy

from catena import api
from catena.api import resize_like
from std_math_nodes.math_node import MathNode


class SubtractNode(MathNode):
    """A node that subtracts one input modifier from another."""

    def __init__(self) -> None:
        super().__init__(title="Subtract")

    def _build(self) -> None:
        self.port_in_a = self.add_port(api.PortType.INPUT, "A", api.PortDataType.VECTOR4)
        self.port_in_b = self.add_port(api.PortType.INPUT, "B", api.PortDataType.VECTOR4)
        self.port_out = self.add_port(
            api.PortType.OUTPUT, "Output", api.PortDataType.VECTOR4
        )
        super()._build()

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        """
        Subtract modifier B from modifier A per-pixel.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Expects keys "A" and "B",
                each containing a float32 modifier. Values may fall below 0 and
                should be clamped downstream if needed.
        Returns:
            numpy.ndarray | None: The subtracted float32 modifier, or whichever
                input is non-None if only one is provided.
        """
        image_a = inputs.get("A")
        image_b = inputs.get("B")
        data_type = self.get_field_value("data_type")

        if image_a is None and image_b is None:
            return None
        if image_a is None:
            return image_b
        if image_b is None:
            return image_a

        if image_a.shape != image_b.shape:
            image_b = resize_like(image_b, image_a)

        if data_type in (api.PortDataType.FLOAT, api.PortDataType.INT, api.PortDataType.VECTOR1):
            if image_a.ndim == 3:
                image_a = image_a.mean(axis=2, keepdims=True)
            if image_b.ndim == 3:
                image_b = image_b.mean(axis=2, keepdims=True)

        return (image_a - image_b).astype(numpy.float32)
