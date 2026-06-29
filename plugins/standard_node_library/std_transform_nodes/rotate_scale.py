from typing import Optional

import cv2
import numpy

from catena import api
from std_transform_nodes import IMAGE_NODE_COLOR


class RotateScaleNode(api.CatenaNode):
    """A node that rotates and non-uniformly scales an input modifier."""

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:

        super().__init__(title="Rotate Scale")

    def _build(self) -> None:
        self.port_in = self.add_port(api.PortType.INPUT, "Input")
        self.port_out = self.add_port(api.PortType.OUTPUT, "Output")

        self.add_field(
            api.FieldDefinition(
                name="angle",
                label="Angle",
                field_type=api.FieldType.FLOAT,
                default=0.0,
                min_value=-360.0,
                max_value=360.0,
            )
        )
        self.add_field(
            api.FieldDefinition(
                name="scale_x",
                label="Scale X",
                field_type=api.FieldType.FLOAT,
                default=1.0,
                min_value=0.01,
                max_value=999999.0,
            )
        )
        self.add_field(
            api.FieldDefinition(
                name="scale_y",
                label="Scale Y",
                field_type=api.FieldType.FLOAT,
                default=1.0,
                min_value=0.01,
                max_value=999999.0,
            )
        )

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        """
        Rotate an input modifier by an arbitrary angle.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Expects key "Input"
                containing a float32 modifier.
        Returns:
            numpy.ndarray | None: The rotated float32 modifier.
        """
        angle = self.get_field_value("angle")
        scale_x = self.get_field_value("scale_x")
        scale_y = self.get_field_value("scale_y")

        image = inputs.get("Input")
        if image is None:
            return None

        height, width = image.shape[:2]
        center = (width / 2.0, height / 2.0)

        radians = numpy.deg2rad(angle)
        cos_a = numpy.cos(radians)
        sin_a = numpy.sin(radians)

        matrix = numpy.array(
            [
                [cos_a * scale_x, sin_a * scale_y, 0.0],
                [-sin_a * scale_x, cos_a * scale_y, 0.0],
            ],
            dtype=numpy.float32,
        )

        matrix[0, 2] = center[0] - matrix[0, 0] * center[0] - matrix[0, 1] * center[1]
        matrix[1, 2] = center[1] - matrix[1, 0] * center[0] - matrix[1, 1] * center[1]

        return cv2.warpAffine(image, matrix, (width, height)).astype(numpy.float32)
