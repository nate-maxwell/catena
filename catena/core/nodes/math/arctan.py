from typing import Optional

import numpy
from PySide6TK.Nodes.node import FieldDefinition
from PySide6TK.Nodes.node import FieldType
from PySide6TK.Nodes.node import PortType

from catena.core.nodes.base import CatenaNode
from catena.core.nodes.math import IMAGE_NODE_COLOR


class ArctangentNode(CatenaNode):
    """A node that applies an arctangent remap, either as a generator or as a remap of an input."""

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        super().__init__(title="Arctangent")

    def _build(self) -> None:
        self.port_in = self.add_port(PortType.INPUT, "Input")
        self.port_out = self.add_port(PortType.OUTPUT, "Output")

        self.add_field(
            FieldDefinition(
                name="frequency",
                label="Frequency",
                field_type=FieldType.FLOAT,
                default=8.0,
                min_value=0.1,
                max_value=64.0,
            )
        )
        self.add_field(
            FieldDefinition(
                name="phase",
                label="Phase",
                field_type=FieldType.FLOAT,
                default=0.0,
                min_value=-360.0,
                max_value=360.0,
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
        self.add_field(
            FieldDefinition(
                name="scale",
                label="Scale",
                field_type=FieldType.FLOAT,
                default=1.0,
                min_value=0.01,
                max_value=20.0,
            )
        )

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        image = inputs.get("Input")

        frequency = self.get_field_value("frequency")
        phase = self.get_field_value("phase")
        angle = self.get_field_value("angle")
        scale = self.get_field_value("scale")

        width, height = 512, 512
        if image is not None:
            height, width = image.shape[:2]

        if image is None:
            y_idx, x_idx = numpy.indices((height, width), dtype=numpy.float32)
            radians = numpy.deg2rad(angle)
            direction_x = numpy.cos(radians)
            direction_y = numpy.sin(radians)

            cx, cy = width / 2.0, height / 2.0
            projection = (x_idx - cx) * direction_x + (y_idx - cy) * direction_y
            max_extent = max(width, height)

            phase_rad = numpy.deg2rad(phase)
            wave = numpy.arctan(
                (2 * frequency * projection / max_extent + phase_rad) * scale
            )
            wave = (wave / (numpy.pi / 2.0) + 1.0) * 0.5

            return numpy.repeat(wave[:, :, None], 3, axis=2).astype(numpy.float32)

        gray = image.mean(axis=2)
        phase_rad = numpy.deg2rad(phase)
        centered = (gray - 0.5) * 2.0
        wave = numpy.arctan((frequency * centered + phase_rad) * scale)
        wave = (wave / (numpy.pi / 2.0) + 1.0) * 0.5

        return numpy.repeat(wave[:, :, None], 3, axis=2).astype(numpy.float32)
