from typing import Optional

import cv2
import numpy

from catena import api
from std_modifier_nodes import IMAGE_NODE_COLOR


class RadialBlurNode(api.CatenaNode):
    """A node that blurs pixels outward along radial lines from a center point."""

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:

        super().__init__(title="Radial Blur")

    def _build(self) -> None:
        self.port_in = self.add_port(api.PortType.INPUT, "Input")
        self.port_out = self.add_port(api.PortType.OUTPUT, "Output")

        self.add_field(
            api.FieldDefinition(
                name="intensity",
                label="Intensity",
                field_type=api.FieldType.FLOAT,
                default=40.0,
                min_value=0.0,
                max_value=500.0,
            )
        )
        self.add_field(
            api.FieldDefinition(
                name="samples",
                label="Samples",
                field_type=api.FieldType.INT,
                default=16,
                min_value=2,
                max_value=64,
            )
        )
        self.add_field(
            api.FieldDefinition(
                name="center_x",
                label="Center X",
                field_type=api.FieldType.FLOAT,
                default=0.5,
                min_value=0.0,
                max_value=1.0,
            )
        )
        self.add_field(
            api.FieldDefinition(
                name="center_y",
                label="Center Y",
                field_type=api.FieldType.FLOAT,
                default=0.5,
                min_value=0.0,
                max_value=1.0,
            )
        )

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        """
        Apply radial blur by accumulating samples along the radial direction
        from the center point for each pixel. Each sample displaces the lookup
        position along the pixel's radial vector by an evenly spaced fraction
        of intensity. Pixels at the center receive no displacement.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Must contain key
                "Input" with a float32 BGR image.
        Returns:
            numpy.ndarray | None: A float32 BGR image of shape (H, W, 3)
                with values in [0, 1], or None if no input is provided.
        """

        intensity = self.get_field_value("intensity")
        samples = self.get_field_value("samples")
        center_x = self.get_field_value("center_x")
        center_y = self.get_field_value("center_y")

        image = inputs.get("Input")
        if image is None:
            return None

        image = numpy.clip(image, 0.0, 1.0).astype(numpy.float32)
        h, w = image.shape[:2]

        cx = center_x * w
        cy = center_y * h

        y_idx, x_idx = numpy.mgrid[0:h, 0:w].astype(numpy.float32)
        dx = x_idx - cx
        dy = y_idx - cy
        dist = numpy.sqrt(dx * dx + dy * dy)
        safe_dist = numpy.maximum(dist, 1.0)
        ndx = (dx / safe_dist).astype(numpy.float32)
        ndy = (dy / safe_dist).astype(numpy.float32)

        n = max(2, samples)
        result = numpy.zeros_like(image)
        for i in range(n):
            t = (i / (n - 1) - 0.5) * intensity
            map_x = numpy.clip(x_idx + ndx * t, 0, w - 1)
            map_y = numpy.clip(y_idx + ndy * t, 0, h - 1)
            result += cv2.remap(
                image, map_x, map_y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT
            )

        return numpy.clip(result / n, 0.0, 1.0)
