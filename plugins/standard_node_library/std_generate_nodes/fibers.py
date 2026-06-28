from typing import Optional

import cv2
import numpy

from catena import api
from std_generate_nodes.generator import GeneratorNode


class FibersNode(GeneratorNode):
    """A node that generates long thin fiber streaks."""

    def __init__(self) -> None:
        super().__init__(title="Fibers")

    def _build(self) -> None:
        self.port_out = self.add_port(api.PortType.OUTPUT, "Output")

        self.add_field(
            api.FieldDefinition(
                name="length_min",
                label="Length Min",
                field_type=api.FieldType.INT,
                default=10,
                min_value=1,
                max_value=99999,
            )
        )
        self.add_field(
            api.FieldDefinition(
                name="length_max",
                label="Length Max",
                field_type=api.FieldType.INT,
                default=80,
                min_value=1,
                max_value=99999,
            )
        )
        self.add_field(
            api.FieldDefinition(
                name="softness",
                label="Softness",
                field_type=api.FieldType.FLOAT,
                default=1.0,
                min_value=0.0,
                max_value=10.0,
            )
        )
        self.add_field(
            api.FieldDefinition(
                name="direction",
                label="Direction",
                field_type=api.FieldType.FLOAT,
                default=0.0,
                min_value=-360.0,
                max_value=360.0,
            )
        )
        self.add_field(
            api.FieldDefinition(
                name="seed",
                label="Seed",
                field_type=api.FieldType.INT,
                default=0,
                min_value=0,
                max_value=99999,
            )
        )

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        """
        Generate long thin fiber streaks similar to Photoshop's fibers effect.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Unused; generators
                produce output from parameters only.
        Returns:
            numpy.ndarray | None: A float32 fiber modifier of shape
                (width, height, 3) with values in [0, 1].
        """
        length_min = self.get_field_value("length_min")
        length_max = self.get_field_value("length_max")
        softness = self.get_field_value("softness")
        direction = self.get_field_value("direction")

        seed = self.get_field_value("seed")
        seed = int(seed * 255) if isinstance(seed, float) else int(seed)
        width, height = api.get_texture_resolution()
        rng = numpy.random.default_rng(seed)

        length_min = min(length_min, length_max)
        length_max = max(length_min, length_max)
        if length_min == length_max:
            length_max = length_min + 1

        result = numpy.zeros((height, width), dtype=numpy.float32)

        for x in range(width):
            column = numpy.zeros(height, dtype=numpy.float32)
            y = 0
            while y < height:
                fiber_length = int(rng.uniform(length_min, length_max))
                value = rng.random()
                end = min(y + fiber_length, height)
                column[y:end] = value
                y = end
            result[:, x] = column

        if softness > 0:
            result = cv2.GaussianBlur(result, (0, 0), sigmaX=softness, sigmaY=0)

        if direction != 0.0:
            center = (width / 2.0, height / 2.0)
            matrix = cv2.getRotationMatrix2D(center, direction, 1.0)
            result = cv2.warpAffine(
                result, matrix, (width, height), borderMode=cv2.BORDER_WRAP
            )

        return numpy.repeat(result[:, :, None], 4, axis=2).astype(numpy.float32)
