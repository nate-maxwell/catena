from typing import Optional

import numpy
from PySide6TK.Nodes.node import FieldDefinition
from PySide6TK.Nodes.node import FieldType
from PySide6TK.Nodes.node import PortType

from catena.core.nodes.base import CatenaNode
from catena.core.nodes.image import IMAGE_NODE_COLOR


class MultiplyNode(CatenaNode):
    """A node that multiplies an input image by a image."""

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        super().__init__(title="Multiply", width=180, body_height=40)

    def _build(self) -> None:
        self.port_in = self.add_port(PortType.INPUT, "Image")
        self.port_out = self.add_port(PortType.OUTPUT, "Image")

        self.add_field(
            FieldDefinition(
                name="image",
                label="Color",
                field_type=FieldType.COLOR,
                default=(255, 255, 255, 255),
            )
        )

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        image = inputs.get("Image")
        if image is None:
            return None

        r, g, b, _ = self.get_field_value("image")
        factor = numpy.array([b, g, r], dtype=numpy.float32) / 255.0

        result = image.astype(numpy.float32) * factor
        result = numpy.clip(result, 0, 255).astype(numpy.uint8)
        return result
