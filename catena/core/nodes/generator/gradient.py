from typing import Optional

import numpy
from PySide6TK.Nodes.node import FieldDefinition
from PySide6TK.Nodes.node import FieldType
from PySide6TK.Nodes.node import PortType

from catena.core.nodes.base import CatenaNode
from catena.core.nodes.generator import IMAGE_NODE_COLOR


class GradientNode(CatenaNode):
    """A node that generates a linear gradient between two colors."""

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        super().__init__(title="Gradient", body_height=80)

    def _build(self) -> None:
        self.port_out = self.add_port(PortType.OUTPUT, "Output")

        self.add_field(
            FieldDefinition(
                name="color_a",
                label="Color A",
                field_type=FieldType.COLOR,
                default=(0, 0, 0, 255),
            )
        )
        self.add_field(
            FieldDefinition(
                name="color_b",
                label="Color B",
                field_type=FieldType.COLOR,
                default=(255, 255, 255, 255),
            )
        )
        self.add_field(
            FieldDefinition(
                name="angle",
                label="Angle",
                field_type=FieldType.FLOAT,
                default=0.0,
                min_value=-360.0,
                max_value=360.0,
            )
        )

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        r_a, g_a, b_a, _ = self.get_field_value("color_a")
        r_b, g_b, b_b, _ = self.get_field_value("color_b")
        angle = self.get_field_value("angle")

        width, height = 512, 512

        y_idx, x_idx = numpy.indices((height, width), dtype=numpy.float32)

        radians = numpy.deg2rad(angle)
        direction_x = numpy.cos(radians)
        direction_y = numpy.sin(radians)

        cx, cy = width / 2.0, height / 2.0
        projection = (x_idx - cx) * direction_x + (y_idx - cy) * direction_y

        max_extent = numpy.sqrt(cx**2 + cy**2)
        t = (projection / max_extent + 1.0) / 2.0
        t = numpy.clip(t, 0.0, 1.0)

        color_a = numpy.array([b_a, g_a, r_a], dtype=numpy.float32) / 255.0
        color_b = numpy.array([b_b, g_b, r_b], dtype=numpy.float32) / 255.0

        result = (
            color_a[None, None, :] * (1 - t[:, :, None])
            + color_b[None, None, :] * t[:, :, None]
        )

        return result.astype(numpy.float32)
