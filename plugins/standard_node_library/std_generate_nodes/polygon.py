from typing import Optional

import cv2
import numpy

from catena import api
from std_generate_nodes.generator import GeneratorNode


class PolygonNode(GeneratorNode):
    """A node that generates a regular polygon shape mask."""

    def __init__(self) -> None:
        super().__init__(title="Polygon")

    def _build(self) -> None:
        self.port_out = self.add_port(api.PortType.OUTPUT, "Output")

        self.add_field(
            api.FieldDefinition(
                name="sides",
                label="Sides",
                field_type=api.FieldType.INT,
                default=1,
                min_value=1,
                max_value=64,
            )
        )
        self.add_field(
            api.FieldDefinition(
                name="size",
                label="Size",
                field_type=api.FieldType.FLOAT,
                default=0.5,
                min_value=0.01,
                max_value=1.0,
            )
        )
        self.add_field(
            api.FieldDefinition(
                name="rotation",
                label="Rotation",
                field_type=api.FieldType.FLOAT,
                default=0.0,
                min_value=-360.0,
                max_value=360.0,
            )
        )

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        """
        Generate a regular polygon shape mask.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Unused; generators
                produce output from parameters only.
        Returns:
            numpy.ndarray | None: A float32 mask modifier of shape (width, height, 3)
                with values in [0, 1].
        """
        sides = self.get_field_value("sides")
        size = self.get_field_value("size")
        rotation = self.get_field_value("rotation")
        width, height = api.get_texture_resolution()
        canvas = numpy.zeros((height, width), dtype=numpy.uint8)

        cx, cy = width / 2.0, height / 2.0
        radius = min(width, height) / 2.0 * size

        angles = numpy.deg2rad(numpy.arange(sides) * (360.0 / sides) + rotation - 90.0)
        points = numpy.stack(
            [cx + radius * numpy.cos(angles), cy + radius * numpy.sin(angles)],
            axis=1,
        ).astype(numpy.int32)
        cv2.fillPoly(canvas, [points], 255)

        gray = canvas.astype(numpy.float32) / 255.0
        return numpy.repeat(gray[:, :, None], 4, axis=2).astype(numpy.float32)
