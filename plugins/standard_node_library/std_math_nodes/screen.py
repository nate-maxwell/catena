from typing import Optional

import cv2
import numpy

from catena import api
from catena.api import resize_like
from std_math_nodes.math_node import MathNode


class ScreenNode(MathNode):
    """A node that combines two input images using the screen blend mode."""

    def __init__(self) -> None:
        super().__init__(title="Screen")

    def _build(self) -> None:
        self.port_in_a = self.add_port(
            api.PortType.INPUT, "A", api.PortDataType.VECTOR4
        )
        self.port_in_b = self.add_port(
            api.PortType.INPUT, "B", api.PortDataType.VECTOR4
        )
        self.port_out = self.add_port(
            api.PortType.OUTPUT, "Output", api.PortDataType.VECTOR4
        )
        super()._build()

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        """
        Combine two input images using the screen blend mode.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Expects keys "A" and "B",
                each containing a float32 modifier with values in [0, 1].
        Returns:
            numpy.ndarray | None: The screen-blended float32 modifier, or
                whichever input is non-None if only one is provided.
        """
        image_a = inputs.get("A")
        image_b = inputs.get("B")

        if image_a is None and image_b is None:
            return None
        if image_a is None:
            return image_b
        if image_b is None:
            return image_a

        if image_a.shape != image_b.shape:
            image_b = resize_like(image_b, image_a)

        return (1.0 - (1.0 - image_a) * (1.0 - image_b)).astype(numpy.float32)
