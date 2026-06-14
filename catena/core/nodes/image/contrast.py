from typing import Optional

import cv2
import numpy
from PySide6TK.Nodes.node import FieldDefinition
from PySide6TK.Nodes.node import FieldType
from PySide6TK.Nodes.node import PortType

from catena.core.nodes.base import CatenaNode
from catena.core.nodes.image import IMAGE_NODE_COLOR


class ContrastNode(CatenaNode):
    """A node that adjusts brightness and contrast of an input image."""

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        super().__init__(title="Contrast")

    def _build(self) -> None:
        self.port_in = self.add_port(PortType.INPUT, "Input")
        self.port_out = self.add_port(PortType.OUTPUT, "Output")

        self.add_field(
            FieldDefinition(
                name="contrast",
                label="Contrast",
                field_type=FieldType.FLOAT,
                default=1.0,
                min_value=0.0,
                max_value=4.0,
            )
        )
        self.add_field(
            FieldDefinition(
                name="brightness",
                label="Brightness",
                field_type=FieldType.FLOAT,
                default=0.0,
                min_value=-255.0,
                max_value=255.0,
            )
        )

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        image = inputs.get("Input")
        if image is None:
            return None

        contrast = self.get_field_value("contrast")
        brightness = self.get_field_value("brightness")

        result = image.astype(numpy.float32) * contrast + (brightness / 255.0)
        return result.astype(numpy.float32)
