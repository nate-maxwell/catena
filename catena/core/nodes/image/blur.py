from typing import Optional

import cv2
import numpy
from PySide6TK.Nodes.node import FieldDefinition
from PySide6TK.Nodes.node import FieldType
from PySide6TK.Nodes.node import PortType

from catena.core.nodes.base import CatenaNode
from catena.core.nodes.image import IMAGE_NODE_COLOR


class BlurNode(CatenaNode):
    """A node that applies a Gaussian blur to an input image."""

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        super().__init__(title="Blur")

    def _build(self) -> None:
        self.port_in = self.add_port(PortType.INPUT, "Input")
        self.port_out = self.add_port(PortType.OUTPUT, "Output")

        self.add_field(
            FieldDefinition(
                name="radius",
                label="Radius",
                field_type=FieldType.FLOAT,
                default=2.0,
                min_value=0.0,
                max_value=100.0,
            )
        )

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        image = inputs.get("Input")
        if image is None:
            return None

        radius = self.get_field_value("radius")
        if radius <= 0:
            return image

        result = cv2.GaussianBlur(image, (0, 0), sigmaX=radius, sigmaY=radius)
        return result.astype(numpy.float32)
