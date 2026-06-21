from typing import Optional

import cv2
import numpy
from PySide6TK.Nodes import FieldDefinition
from PySide6TK.Nodes import FieldType
from PySide6TK.Nodes import PortType

from catena.nodes.generate.generator import GeneratorNode
from catena.nodes.node_processor import ProcessorNode
from catena.preferences import preferences


class PolygonProcessor(ProcessorNode):
    """A headless processor that generates a regular polygon shape mask."""

    def __init__(
        self,
        sides: int = 1,
        size: float = 0.5,
        rotation: float = 0.0,
    ) -> None:
        super().__init__()
        self.sides = sides
        self.size = size
        self.rotation = rotation

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        """
        Generate a regular polygon shape mask.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Unused; generators
                produce output from parameters only.
        Returns:
            numpy.ndarray | None: A float32 mask image of shape (width, height, 3)
                with values in [0, 1].
        """
        width = preferences.Preferences().general_preferences.texture_resolution
        height = width
        canvas = numpy.zeros((height, width), dtype=numpy.uint8)

        cx, cy = width / 2.0, height / 2.0
        radius = min(width, height) / 2.0 * self.size

        angles = numpy.deg2rad(
            numpy.arange(self.sides) * (360.0 / self.sides) + self.rotation - 90.0
        )
        points = numpy.stack(
            [cx + radius * numpy.cos(angles), cy + radius * numpy.sin(angles)],
            axis=1,
        ).astype(numpy.int32)
        cv2.fillPoly(canvas, [points], 255)

        gray = canvas.astype(numpy.float32) / 255.0
        return numpy.repeat(gray[:, :, None], 3, axis=2).astype(numpy.float32)


class PolygonNode(GeneratorNode):
    """A node that generates a regular polygon shape mask."""

    def __init__(self) -> None:
        self._processor = PolygonProcessor()
        super().__init__(title="Polygon")

    def _build(self) -> None:
        self.port_out = self.add_port(PortType.OUTPUT, "Output")

        self.add_field(
            FieldDefinition(
                name="sides",
                label="Sides",
                field_type=FieldType.INT,
                default=1,
                min_value=1,
                max_value=64,
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
        self._processor.sides = self.get_field_value("sides")
        self._processor.size = self.get_field_value("size")
        self._processor.rotation = self.get_field_value("rotation")
        return self._processor.process(inputs)
