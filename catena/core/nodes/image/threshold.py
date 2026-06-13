from typing import Optional

import cv2
import numpy
from PySide6TK.Nodes.node import FieldDefinition
from PySide6TK.Nodes.node import FieldType
from PySide6TK.Nodes.node import PortType

from catena.core.nodes.base import CatenaNode
from catena.core.nodes.image import IMAGE_NODE_COLOR


class ThresholdNode(CatenaNode):
    """A node that binarizes an input image based on a threshold value."""

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        super().__init__(title="Threshold", width=180, body_height=40)

    def _build(self) -> None:
        self.port_in = self.add_port(PortType.INPUT, "Input")
        self.port_out = self.add_port(PortType.OUTPUT, "Output")

        self.add_field(
            FieldDefinition(
                name="threshold",
                label="Threshold",
                field_type=FieldType.INT,
                default=128,
                min_value=0,
                max_value=255,
            )
        )
        self.add_field(
            FieldDefinition(
                name="invert",
                label="Invert",
                field_type=FieldType.BOOL,
                default=False,
            )
        )

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        image = inputs.get("Input")
        if image is None:
            return None

        threshold = self.get_field_value("threshold")
        invert = self.get_field_value("invert")

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        mode = cv2.THRESH_BINARY_INV if invert else cv2.THRESH_BINARY
        _, mask = cv2.threshold(gray, threshold, 255, mode)

        result = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
        return result
