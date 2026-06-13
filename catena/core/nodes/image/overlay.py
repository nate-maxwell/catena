from typing import Optional

import cv2
import numpy
from PySide6TK.Nodes.node import FieldDefinition
from PySide6TK.Nodes.node import FieldType
from PySide6TK.Nodes.node import PortType

from catena.core.nodes.base import CatenaNode
from catena.core.nodes.image import IMAGE_NODE_COLOR


class OverlayNode(CatenaNode):
    """A node that blends two input images together by a mix factor."""

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        super().__init__(title="Overlay", body_height=60)

    def _build(self) -> None:
        self.port_in_a = self.add_port(PortType.INPUT, "A")
        self.port_in_b = self.add_port(PortType.INPUT, "B")
        self.port_out = self.add_port(PortType.OUTPUT, "Output")

        self.add_field(
            FieldDefinition(
                name="mix",
                label="Mix",
                field_type=FieldType.FLOAT,
                default=0.5,
                min_value=0.0,
                max_value=1.0,
            )
        )

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        image_a = inputs.get("A")
        image_b = inputs.get("B")

        if image_a is None and image_b is None:
            return None
        if image_a is None:
            return image_b
        if image_b is None:
            return image_a

        if image_a.shape != image_b.shape:
            height, width = image_a.shape[:2]
            image_b = cv2.resize(image_b, (width, height))

        mix = self.get_field_value("mix")
        result = cv2.addWeighted(image_a, 1.0 - mix, image_b, mix, 0.0)
        return result
