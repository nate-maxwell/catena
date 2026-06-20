from typing import Optional

import cv2
import numpy
from PySide6TK.Nodes import FieldDefinition
from PySide6TK.Nodes import FieldType
from PySide6TK.Nodes import PortType

from catena.nodes.base import CatenaNode
from catena.nodes.image import IMAGE_NODE_COLOR


class BevelNode(CatenaNode):
    """A node that adds a beveled highlight/shadow edge to a shape mask."""

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        super().__init__(title="Bevel")

    def _build(self) -> None:
        self.port_in = self.add_port(PortType.INPUT, "Input")
        self.port_out = self.add_port(PortType.OUTPUT, "Output")

        self.add_field(
            FieldDefinition(
                name="distance",
                label="Distance",
                field_type=FieldType.FLOAT,
                default=10.0,
                min_value=1.0,
                max_value=100.0,
            )
        )
        self.add_field(
            FieldDefinition(
                name="angle",
                label="Angle",
                field_type=FieldType.FLOAT,
                default=45.0,
                min_value=0.0,
                max_value=360.0,
            )
        )
        self.add_field(
            FieldDefinition(
                name="depth",
                label="Depth",
                field_type=FieldType.FLOAT,
                default=1.0,
                min_value=-5.0,
                max_value=5.0,
            )
        )
        self.add_field(
            FieldDefinition(
                name="soft",
                label="Soft",
                field_type=FieldType.BOOL,
                default=True,
            )
        )

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        image = inputs.get("Input")
        if image is None:
            return None

        distance = self.get_field_value("distance")
        depth = self.get_field_value("depth")
        soft = self.get_field_value("soft")

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

        result = numpy.repeat(height_field[:, :, None], 3, axis=2).astype(numpy.float32)
        return result
