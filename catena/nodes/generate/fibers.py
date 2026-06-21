from typing import Optional

import cv2
import numpy
from PySide6TK.Nodes import FieldDefinition
from PySide6TK.Nodes import FieldType
from PySide6TK.Nodes import PortType

from catena.nodes.generate.generator import GeneratorNode
from catena.nodes.node_processor import ProcessorNode
from catena.preferences import preferences


class FibersProcessor(ProcessorNode):
    """A headless processor that generates long thin fiber streaks."""

    def __init__(
        self,
        length_min: int = 10,
        length_max: int = 80,
        softness: float = 1.0,
        direction: float = 0.0,
        seed: int = 0,
    ) -> None:
        super().__init__()
        self.length_min = length_min
        self.length_max = length_max
        self.softness = softness
        self.direction = direction
        self.seed = seed

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        """
        Generate long thin fiber streaks similar to Photoshop's fibers effect.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Unused; generators
                produce output from parameters only.
        Returns:
            numpy.ndarray | None: A float32 fiber image of shape
                (width, height, 3) with values in [0, 1].
        """
        width = preferences.Preferences().general_preferences.texture_resolution
        height = width
        rng = numpy.random.default_rng(self.seed)

        length_min = min(self.length_min, self.length_max)
        length_max = max(self.length_min, self.length_max)
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

        if self.softness > 0:
            result = cv2.GaussianBlur(result, (0, 0), sigmaX=self.softness, sigmaY=0)

        if self.direction != 0.0:
            center = (width / 2.0, height / 2.0)
            matrix = cv2.getRotationMatrix2D(center, self.direction, 1.0)
            result = cv2.warpAffine(
                result, matrix, (width, height), borderMode=cv2.BORDER_WRAP
            )

        return numpy.repeat(result[:, :, None], 3, axis=2).astype(numpy.float32)


class FibersNode(GeneratorNode):
    """A node that generates long thin fiber streaks."""

    def __init__(self) -> None:
        self._processor = FibersProcessor()
        super().__init__(title="Fibers")

    def _build(self) -> None:
        self.port_out = self.add_port(PortType.OUTPUT, "Output")

        self.add_field(
            FieldDefinition(
                name="length_min",
                label="Length Min",
                field_type=FieldType.INT,
                default=10,
                min_value=1,
                max_value=99999,
            )
        )
        self.add_field(
            FieldDefinition(
                name="length_max",
                label="Length Max",
                field_type=FieldType.INT,
                default=80,
                min_value=1,
                max_value=99999,
            )
        )
        self.add_field(
            FieldDefinition(
                name="softness",
                label="Softness",
                field_type=FieldType.FLOAT,
                default=1.0,
                min_value=0.0,
                max_value=10.0,
            )
        )
        self.add_field(
            FieldDefinition(
                name="direction",
                label="Direction",
                field_type=FieldType.FLOAT,
                default=0.0,
                min_value=-360.0,
                max_value=360.0,
            )
        )
        self.add_field(
            FieldDefinition(
                name="seed",
                label="Seed",
                field_type=FieldType.INT,
                default=0,
                min_value=0,
                max_value=99999,
            )
        )

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        self._processor.length_min = self.get_field_value("length_min")
        self._processor.length_max = self.get_field_value("length_max")
        self._processor.softness = self.get_field_value("softness")
        self._processor.direction = self.get_field_value("direction")
        self._processor.seed = self.get_field_value("seed")
        return self._processor.process(inputs)
