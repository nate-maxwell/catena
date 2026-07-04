from typing import Optional

import cv2
import numpy

from catena import api
from catena.api import resize_like
from std_math_nodes.math_node import MathNode


class DivideNode(MathNode):
    """A node that divides one input modifier by another."""

    def __init__(self) -> None:
        super().__init__(title="Divide")

    def _build(self) -> None:
        self.port_in_a = self.add_port(api.PortType.INPUT, "A", api.PortDataType.VECTOR4)
        self.port_in_b = self.add_port(api.PortType.INPUT, "B", api.PortDataType.VECTOR4)
        self.port_out = self.add_port(
            api.PortType.OUTPUT, "Output", api.PortDataType.VECTOR4
        )
        super()._build()

    @staticmethod
    def _collapse_scalar(image: numpy.ndarray) -> numpy.ndarray:
        if image.ndim == 3:
            return image.mean(axis=2, keepdims=True)
        return image

    @staticmethod
    def _collapse_uniform_scalar(image: numpy.ndarray) -> numpy.ndarray:
        image = DivideNode._collapse_scalar(image).astype(numpy.float32)
        if image.size == 0:
            return image

        minimum = float(numpy.min(image))
        maximum = float(numpy.max(image))
        if abs(maximum - minimum) <= 1e-6:
            return numpy.full((1, 1, 1), float(image.mean()), dtype=numpy.float32)

        return image

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        """
        Divide modifier A by modifier B per-pixel.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Expects keys "A" and "B",
                each containing a float32 modifier. Both must be connected.
        Returns:
            numpy.ndarray | None: The divided float32 modifier. Values may
                exceed [0, 1] and should be clamped downstream if needed.
                Returns None if either input is missing.
        """
        image_a = inputs.get("A")
        image_b = inputs.get("B")
        data_type = self.get_field_value("data_type")

        if image_a is None or image_b is None:
            return None

        if data_type in (api.PortDataType.FLOAT, api.PortDataType.INT, api.PortDataType.VECTOR1):
            image_a = self._collapse_uniform_scalar(image_a)
            image_b = self._collapse_uniform_scalar(image_b)

        if image_a.shape != image_b.shape:
            if image_a.shape == (1, 1, 1):
                image_a = numpy.full(image_b.shape, float(image_a.mean()), dtype=numpy.float32)
            elif image_b.shape == (1, 1, 1):
                image_b = numpy.full(image_a.shape, float(image_b.mean()), dtype=numpy.float32)
            else:
                image_b = resize_like(image_b, image_a)

        a = image_a.astype(numpy.float32)
        b = numpy.where(image_b == 0, 1e-6, image_b.astype(numpy.float32))

        return (a / b).astype(numpy.float32)
