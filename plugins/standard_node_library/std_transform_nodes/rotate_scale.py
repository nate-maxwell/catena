from typing import Optional

import cv2
import numpy

from catena import api
from std_transform_nodes import IMAGE_NODE_COLOR


class RotateScaleNode(api.CatenaNode):
    """A node that rotates an input modifier by an arbitrary angle."""

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
                name="scale",
                label="Scale",
                field_type=api.FieldType.FLOAT,
                default=1.0,
                min_value=0.01,
                max_value=10.0,
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
        scale = self.get_field_value("scale")

        image = inputs.get("Input")
        if image is None:
            return None

        height, width = image.shape[:2]
        center = (width / 2.0, height / 2.0)

        matrix = cv2.getRotationMatrix2D(center, angle, scale)
        return cv2.warpAffine(image, matrix, (width, height)).astype(numpy.float32)
