from typing import Optional

import cv2
import numpy
from PySide6TK.Nodes.node import FieldDefinition
from PySide6TK.Nodes.node import FieldType
from PySide6TK.Nodes.node import PortType

from catena.core.nodes.base import CatenaNode
from catena.core.nodes.image import IMAGE_NODE_COLOR


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

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        image = inputs.get("Input")
        if image is None:
            return None

        distance = self.get_field_value("distance")
        angle = self.get_field_value("angle")

        if image.ndim == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        mask = (gray > 127).astype(numpy.uint8) * 255

        depth = self.get_field_value("depth")

        dist_inside = cv2.distanceTransform(mask, cv2.DIST_L2, 5)
        dist_outside = cv2.distanceTransform(255 - mask, cv2.DIST_L2, 5)

        signed_dist = (dist_inside - dist_outside) * depth

        height_field = numpy.clip(signed_dist / distance, -1.0, 1.0)
        height_field = (height_field + 1.0) * 0.5

        gy, gx = numpy.gradient(height_field)

        radians = numpy.deg2rad(angle)
        light_x = numpy.cos(radians)
        light_y = numpy.sin(radians)

        normal_strength = numpy.sqrt(gx * gx + gy * gy + 1.0)
        nx = -gx / normal_strength
        ny = -gy / normal_strength
        nz = 1.0 / normal_strength

        lighting = nx * light_x + ny * light_y + nz * 0.5
        lighting = numpy.clip(lighting, 0.0, 1.0)

        shaded = (lighting * 255.0).astype(numpy.uint8)
        result = cv2.cvtColor(shaded, cv2.COLOR_GRAY2BGR)
        return result
