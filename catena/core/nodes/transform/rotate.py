from typing import Optional

import cv2
import numpy
from PySide6TK.Nodes.node import FieldDefinition
from PySide6TK.Nodes.node import FieldType
from PySide6TK.Nodes.node import PortType

from catena.core.nodes.base import CatenaNode
from catena.core.nodes.transform import IMAGE_NODE_COLOR


class RotateNode(CatenaNode):
    """A node that rotates an input image by an arbitrary angle."""

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        super().__init__(title="Rotate", width=180, body_height=60)

    def _build(self) -> None:
        self.port_in = self.add_port(PortType.INPUT, "Input")
        self.port_out = self.add_port(PortType.OUTPUT, "Output")

        self.add_field(
            FieldDefinition(
                name="angle",
                label="Angle",
                field_type=FieldType.FLOAT,
                default=0.0,
                min_value=-360.0,
                max_value=360.0,
            )
        )
        self.add_field(
            FieldDefinition(
                name="scale",
                label="Scale",
                field_type=FieldType.FLOAT,
                default=1.0,
                min_value=0.01,
                max_value=10.0,
            )
        )

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        image = inputs.get("Input")
        if image is None:
            return None

        angle = self.get_field_value("angle")
        scale = self.get_field_value("scale")

        height, width = image.shape[:2]
        center = (width / 2.0, height / 2.0)

        matrix = cv2.getRotationMatrix2D(center, angle, scale)
        result = cv2.warpAffine(image, matrix, (width, height))
        return result
