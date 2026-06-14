from typing import Optional

import cv2
import numpy
from PySide6TK.Nodes.node import FieldDefinition
from PySide6TK.Nodes.node import FieldType
from PySide6TK.Nodes.node import PortType

from catena.core.nodes.base import CatenaNode
from catena.core.nodes.generator import IMAGE_NODE_COLOR


class ShapeNode(CatenaNode):
    """A node that generates a circle or regular polygon shape mask."""

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        super().__init__(title="Shape", body_height=80)

    def _build(self) -> None:
        self.port_out = self.add_port(PortType.OUTPUT, "Output")

        self.add_field(
            FieldDefinition(
                name="sides",
                label="Sides",
                field_type=FieldType.INT,
                default=0,
                min_value=0,
                max_value=32,
            )
        )
        self.add_field(
            FieldDefinition(
                name="size",
                label="Size",
                field_type=FieldType.FLOAT,
                default=0.5,
                min_value=0.01,
                max_value=1.0,
            )
        )
        self.add_field(
            FieldDefinition(
                name="rotation",
                label="Rotation",
                field_type=FieldType.FLOAT,
                default=0.0,
                min_value=-360.0,
                max_value=360.0,
            )
        )

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        sides = self.get_field_value("sides")
        size = self.get_field_value("size")
        rotation = self.get_field_value("rotation")

        width, height = 512, 512
        canvas = numpy.zeros((height, width), dtype=numpy.uint8)

        cx, cy = width / 2.0, height / 2.0
        radius = min(width, height) / 2.0 * size

        if sides <= 0:
            cv2.circle(canvas, (int(cx), int(cy)), int(radius), 255, -1)
        else:
            angles = numpy.deg2rad(
                numpy.arange(sides) * (360.0 / sides) + rotation - 90.0
            )
            points = numpy.stack(
                [cx + radius * numpy.cos(angles), cy + radius * numpy.sin(angles)],
                axis=1,
            ).astype(numpy.int32)
            cv2.fillPoly(canvas, [points], 255)

        gray = canvas.astype(numpy.float32) / 255.0
        result = numpy.repeat(gray[:, :, None], 3, axis=2).astype(numpy.float32)
        return result
