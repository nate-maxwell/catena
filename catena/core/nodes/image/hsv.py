from typing import Optional

import cv2
import numpy
from PySide6TK.Nodes.node import FieldDefinition
from PySide6TK.Nodes.node import FieldType
from PySide6TK.Nodes.node import PortType

from catena.core.nodes.base import CatenaNode
from catena.core.nodes.image import IMAGE_NODE_COLOR


class HSVNode(CatenaNode):
    """A node that shifts hue, saturation, and value of an input image."""

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        super().__init__(title="HSV")

    def _build(self) -> None:
        self.port_in = self.add_port(PortType.INPUT, "Input")
        self.port_out = self.add_port(PortType.OUTPUT, "Output")

        self.add_field(
            FieldDefinition(
                name="hue_shift",
                label="Hue Shift",
                field_type=FieldType.INT,
                default=0,
                min_value=-180,
                max_value=180,
            )
        )
        self.add_field(
            FieldDefinition(
                name="saturation",
                label="Saturation",
                field_type=FieldType.FLOAT,
                default=1.0,
                min_value=0.0,
                max_value=3.0,
            )
        )
        self.add_field(
            FieldDefinition(
                name="value",
                label="Value",
                field_type=FieldType.FLOAT,
                default=1.0,
                min_value=0.0,
                max_value=3.0,
            )
        )

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        image = inputs.get("Input")
        if image is None:
            return None

        hue_shift = self.get_field_value("hue_shift")
        saturation = self.get_field_value("saturation")
        value = self.get_field_value("value")

        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV).astype(numpy.int16)

        hsv[..., 0] = (hsv[..., 0] + hue_shift) % 180
        hsv[..., 1] = numpy.clip(hsv[..., 1] * saturation, 0, 255)
        hsv[..., 2] = numpy.clip(hsv[..., 2] * value, 0, 255)

        result = cv2.cvtColor(hsv.astype(numpy.uint8), cv2.COLOR_HSV2BGR)
        return result
