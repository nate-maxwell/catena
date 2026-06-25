from typing import Optional

import cv2
import numpy
from PySide6TK.Nodes import FieldDefinition
from PySide6TK.Nodes import FieldType
from PySide6TK.Nodes import PortType

from catena.nodes.generate.generator import GeneratorNode
from catena.nodes.node_processor import ProcessorNode
from catena.preferences import preferences


class BNWSpotsProcessor(ProcessorNode):
    """A headless processor that generates random black and white spots."""

    def __init__(
        self,
        density: float = 0.01,
        size: int = 4,
        seed: int = 0,
    ) -> None:
        super().__init__()
        self.density = density
        self.size = size
        self.seed = seed

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]] | None = None
    ) -> Optional[numpy.ndarray]:
        """
        Generate random black and white spots with seamless tiling.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Unused; generators
                produce output from parameters only.
        Returns:
            numpy.ndarray | None: A float32 modifier of shape (width, height, 3)
                with values in [0, 1].
        """
        width = preferences.Preferences().general_preferences.texture_resolution
        height = width
        rng = numpy.random.default_rng(self.seed)

        canvas = numpy.full((height, width), 128, dtype=numpy.uint8)

        num_spots = int(width * height * self.density)
        xs = rng.integers(0, width, num_spots)
        ys = rng.integers(0, height, num_spots)
        colors = rng.choice([0, 255], num_spots)

        offsets = [
            (-width, -height),
            (0, -height),
            (width, -height),
            (-width, 0),
            (0, 0),
            (width, 0),
            (-width, height),
            (0, height),
            (width, height),
        ]

        for x, y, color in zip(xs, ys, colors):
            for ox, oy in offsets:
                px, py = int(x) + ox, int(y) + oy
                if (
                    -self.size <= px <= width + self.size
                    and -self.size <= py <= height + self.size
                ):
                    cv2.circle(canvas, (px, py), self.size, int(color), -1)

        gray = canvas.astype(numpy.float32) / 255.0
        return numpy.repeat(gray[:, :, None], 4, axis=2).astype(numpy.float32)


class BNWSpotsNode(GeneratorNode):
    """A node that generates random black and white spots."""

    def __init__(self) -> None:
        self._processor = BNWSpotsProcessor()
        super().__init__(title="BnW Spots")

    def _build(self) -> None:
        self.port_out = self.add_port(PortType.OUTPUT, "Output")

        self.add_field(
            FieldDefinition(
                name="density",
                label="Density",
                field_type=FieldType.FLOAT,
                default=0.01,
                min_value=0.0001,
                max_value=100,
            )
        )
        self.add_field(
            FieldDefinition(
                name="size",
                label="Size",
                field_type=FieldType.INT,
                default=4,
                min_value=1,
                max_value=64,
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
        self._processor.density = self.get_field_value("density")
        self._processor.size = self.get_field_value("size")

        seed = self.get_field_value("seed")
        self._processor.seed = int(seed * 255) if isinstance(seed, float) else int(seed)

        return self._processor.process(inputs)
