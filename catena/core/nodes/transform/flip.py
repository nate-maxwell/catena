from typing import Optional

import cv2
import numpy
from PySide6TK.Nodes.node import FieldDefinition
from PySide6TK.Nodes.node import FieldType
from PySide6TK.Nodes.node import PortType

from catena.core.nodes.base import CatenaNode
from catena.core.nodes.transform import IMAGE_NODE_COLOR


class FlipNode(CatenaNode):
    """A node that flips an input image horizontally, vertically, or both."""

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        super().__init__(title="Flip", width=180, body_height=40)

    def _build(self) -> None:
        self.port_in = self.add_port(PortType.INPUT, "Image")
        self.port_out = self.add_port(PortType.OUTPUT, "Image")

        self.add_field(
            FieldDefinition(
                name="direction",
                label="Direction",
                field_type=FieldType.CHOICE,
                default="Horizontal",
                options=["Horizontal", "Vertical", "Both"],
            )
        )

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        image = inputs.get("Image")
        if image is None:
            return None

        direction = self.get_field_value("direction")
        flip_codes = {"Horizontal": 1, "Vertical": 0, "Both": -1}
        flip_code = flip_codes[direction]

        result = cv2.flip(image, flip_code)
        return result
