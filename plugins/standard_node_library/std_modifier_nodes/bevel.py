from typing import Optional

import cv2
import numpy

from std_modifier_nodes import IMAGE_NODE_COLOR
from catena import api


class BevelNode(api.CatenaNode):
    """A node that adds a beveled highlight/shadow edge to a shape mask."""

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:

        super().__init__(title="Bevel")

    def _build(self) -> None:
        self.port_in = self.add_port(api.PortType.INPUT, "Input")
        self.port_out = self.add_port(api.PortType.OUTPUT, "Output")

        self.add_field(
            api.FieldDefinition(
                name="distance",
                label="Distance",
                field_type=api.FieldType.FLOAT,
                default=10.0,
                min_value=1.0,
                max_value=100.0,
            )
        )
        self.add_field(
            api.FieldDefinition(
                name="depth",
                label="Depth",
                field_type=api.FieldType.FLOAT,
                default=1.0,
                min_value=-5.0,
                max_value=5.0,
            )
        )
        self.add_field(
            api.FieldDefinition(
                name="soft",
                label="Soft",
                field_type=api.FieldType.BOOL,
                default=True,
            )
        )

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        """
        Generate a height-map bevel from a shape mask.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Expects key "Input"
                containing a float32 shape mask.
        Returns:
            numpy.ndarray | None: A float32 height map of shape (H, W, 3)
                with values in [0, 1]. Background is black, shape interior
                is white, with a beveled transition at the boundary.
        """
        distance = self.get_field_value("distance")
        depth = self.get_field_value("depth")
        soft = self.get_field_value("soft")
        image = inputs.get("Input")
        if image is None:
            return None

        if image.ndim == 3:
            gray = image.mean(axis=2)
        else:
            gray = image

        mask = (gray > 0.5).astype(numpy.uint8) * 255

        corner_radius = max(1, int(distance * 0.6))
        kernel_size = corner_radius * 2 + 1
        kernel = cv2.getStructuringElement(
            cv2.MORPH_ELLIPSE, (kernel_size, kernel_size)
        )

        mask_rounded = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask_rounded = cv2.morphologyEx(mask_rounded, cv2.MORPH_CLOSE, kernel)

        dist_inside = cv2.distanceTransform(mask_rounded, cv2.DIST_L2, 5)
        dist_outside = cv2.distanceTransform(255 - mask_rounded, cv2.DIST_L2, 5)

        signed_dist = (dist_inside - dist_outside) * depth

        if soft:
            height_field = numpy.tanh(signed_dist / distance)
        else:
            height_field = numpy.clip(signed_dist / distance, -1.0, 1.0)

        height_field = (height_field + 1.0) * 0.5

        return numpy.repeat(height_field[:, :, None], 4, axis=2).astype(numpy.float32)
