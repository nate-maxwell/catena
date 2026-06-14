from typing import Optional

import cv2
import numpy
from PySide6TK.Nodes.node import FieldDefinition
from PySide6TK.Nodes.node import FieldType
from PySide6TK.Nodes.node import PortType

from catena.core.nodes.base import CatenaNode
from catena.core.nodes.image import IMAGE_NODE_COLOR


class SlopeBlurNode(CatenaNode):
    """A node that blurs an image along the gradient of a slope/height map."""

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        super().__init__(title="Slope Blur")

    def _build(self) -> None:
        self.port_in = self.add_port(PortType.INPUT, "Input")
        self.port_in_slope = self.add_port(PortType.INPUT, "Slope")
        self.port_out = self.add_port(PortType.OUTPUT, "Output")

        self.add_field(
            FieldDefinition(
                name="intensity",
                label="Intensity",
                field_type=FieldType.FLOAT,
                default=10.0,
                min_value=0.0,
                max_value=100.0,
            )
        )
        self.add_field(
            FieldDefinition(
                name="samples",
                label="Samples",
                field_type=FieldType.INT,
                default=8,
                min_value=1,
                max_value=32,
            )
        )

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        image = inputs.get("Input")
        slope = inputs.get("Slope")

        if image is None:
            return None

        intensity = self.get_field_value("intensity")
        samples = self.get_field_value("samples")

        if intensity <= 0 or slope is None:
            return image

        height, width = image.shape[:2]

        if slope.shape[:2] != (height, width):
            slope = cv2.resize(slope, (width, height))

        if slope.ndim == 3:
            slope_gray = slope.mean(axis=2)
        else:
            slope_gray = slope

        gy, gx = numpy.gradient(slope_gray)

        grad_max = max(numpy.abs(gx).max(), numpy.abs(gy).max(), 1e-6)
        gx = gx / grad_max
        gy = gy / grad_max

        y_idx, x_idx = numpy.indices((height, width), dtype=numpy.float32)

        accum = numpy.zeros_like(image, dtype=numpy.float32)

        for i in range(samples):
            t = (i / max(samples - 1, 1)) - 0.5

            map_x = (x_idx + gx * intensity * t).astype(numpy.float32)
            map_y = (y_idx + gy * intensity * t).astype(numpy.float32)

            sample = cv2.remap(
                image,
                map_x,
                map_y,
                interpolation=cv2.INTER_LINEAR,
                borderMode=cv2.BORDER_REFLECT,
            )
            accum += sample

        result = accum / samples
        return result.astype(numpy.float32)
