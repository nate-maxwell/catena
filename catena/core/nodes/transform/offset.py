from typing import Optional

import numpy
from PySide6TK.Nodes.node import FieldDefinition
from PySide6TK.Nodes.node import FieldType
from PySide6TK.Nodes.node import PortType

from catena.core.nodes.base import CatenaNode
from catena.core.nodes.transform import IMAGE_NODE_COLOR

NODE_TYPE = "Offset"


class OffsetNode(CatenaNode):
    """A node that offsets an input image, optionally wrapping content around."""

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        super().__init__(title="Offset", width=180, body_height=100)

    def _build(self) -> None:
        self.port_in = self.add_port(PortType.INPUT, "Image")
        self.port_out = self.add_port(PortType.OUTPUT, "Image")

        self.add_field(
            FieldDefinition(
                name="offset_x",
                label="X",
                field_type=FieldType.INT,
                default=0,
            )
        )
        self.add_field(
            FieldDefinition(
                name="offset_y",
                label="Y",
                field_type=FieldType.INT,
                default=0,
            )
        )
        self.add_field(
            FieldDefinition(
                name="wrap",
                label="Wrap",
                field_type=FieldType.BOOL,
                default=True,
            )
        )

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        image = inputs.get("Image")
        if image is None:
            return None

        dx = self.get_field_value("offset_x")
        dy = self.get_field_value("offset_y")
        wrap = self.get_field_value("wrap")

        if wrap:
            result = numpy.roll(image, shift=(dy, dx), axis=(0, 1))
        else:
            result = numpy.zeros_like(image)
            height, width = image.shape[:2]

            src_x0 = max(0, -dx)
            src_x1 = min(width, width - dx)
            src_y0 = max(0, -dy)
            src_y1 = min(height, height - dy)

            dst_x0 = max(0, dx)
            dst_x1 = dst_x0 + (src_x1 - src_x0)
            dst_y0 = max(0, dy)
            dst_y1 = dst_y0 + (src_y1 - src_y0)

            if src_x1 > src_x0 and src_y1 > src_y0:
                result[dst_y0:dst_y1, dst_x0:dst_x1] = image[
                    src_y0:src_y1, src_x0:src_x1
                ]

        return result
