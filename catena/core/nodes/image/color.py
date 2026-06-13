from typing import Optional

import numpy
from PySide6TK.Nodes.node import FieldDefinition
from PySide6TK.Nodes.node import FieldType
from PySide6TK.Nodes.node import PortType

from catena.core.nodes.base import CatenaNode
from catena.core.nodes.image import IMAGE_NODE_COLOR


class ColorNode(CatenaNode):
    """A node that outputs a solid color image."""

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        super().__init__(title="Color", width=120, body_height=20)

    def _build(self) -> None:
        self.port_out = self.add_port(PortType.OUTPUT, "Color")

        self.add_field(
            FieldDefinition(
                name="color",
                label="Color",
                field_type=FieldType.COLOR,
                default=(255, 255, 255, 255),
            )
        )

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        r, g, b, _ = self.get_field_value("color")

        width, height = 512, 512
        result = numpy.zeros((height, width, 3), dtype=numpy.uint8)
        result[:, :] = (b, g, r)

        return result
