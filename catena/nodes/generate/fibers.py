from typing import Optional

import cv2
import numpy
from PySide6TK.Nodes import FieldDefinition
from PySide6TK.Nodes import FieldType
from PySide6TK.Nodes import PortType

from catena.nodes.generate.generator import GeneratorNode
from catena.nodes.node_processor import ProcessorNode


class FibersProcessor(ProcessorNode):
    """A headless processor that generates a fiber/wood grain pattern."""

    def __init__(
        self,
        scale: float = 64.0,
        octaves: int = 4,
        direction: float = 0.0,
        distortion: float = 2.0,
        seed: int = 0,
    ) -> None:
        super().__init__()
        self.scale = scale
        self.octaves = octaves
        self.direction = direction
        self.distortion = distortion
        self.seed = seed

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        """
        Generate a fiber pattern by distorting parallel lines with noise.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Unused; generators
                produce output from parameters only.
        Returns:
            numpy.ndarray | None: A float32 fiber image of shape
                (512, 512, 3) with values in [0, 1].
        """
        width, height = 512, 512
        rng = numpy.random.default_rng(self.seed)

        y_idx, x_idx = numpy.indices((height, width), dtype=numpy.float32)

        radians = numpy.deg2rad(self.direction)
        projection = x_idx * numpy.cos(radians) + y_idx * numpy.sin(radians)

        noise = numpy.zeros((height, width), dtype=numpy.float32)
        amplitude = 1.0
        max_amplitude = 0.0
        current_scale = self.scale

        for i in range(self.octaves):
            grid_h = max(2, int(round(height / current_scale)))
            grid_w = max(2, int(round(width / current_scale)))
            lattice = rng.random((grid_h, grid_w)).astype(numpy.float32)

            ys = numpy.linspace(0, grid_h, height, endpoint=False)
            xs = numpy.linspace(0, grid_w, width, endpoint=False)

            y0 = numpy.floor(ys).astype(int) % grid_h
            x0 = numpy.floor(xs).astype(int) % grid_w
            y1 = (y0 + 1) % grid_h
            x1 = (x0 + 1) % grid_w

            fy = (ys - numpy.floor(ys))[:, None]
            fx = (xs - numpy.floor(xs))[None, :]

            def smooth(t: numpy.ndarray) -> numpy.ndarray:
                return t * t * (3 - 2 * t)

            sy, sx = smooth(fy), smooth(fx)

            tl = lattice[numpy.ix_(y0, x0)]
            tr = lattice[numpy.ix_(y0, x1)]
            bl = lattice[numpy.ix_(y1, x0)]
            br = lattice[numpy.ix_(y1, x1)]

            top = tl * (1 - sx) + tr * sx
            bottom = bl * (1 - sx) + br * sx
            noise += (top * (1 - sy) + bottom * sy) * amplitude

            max_amplitude += amplitude
            amplitude *= 0.5
            current_scale = max(current_scale * 0.5, 2.0)

        noise /= max_amplitude

        distorted = projection / self.scale + noise * self.distortion
        fibers = numpy.sin(distorted * numpy.pi) * 0.5 + 0.5

        result = numpy.repeat(fibers[:, :, None], 3, axis=2).astype(numpy.float32)
        return result


class FibersNode(GeneratorNode):
    """A node that generates a fiber/wood grain pattern."""

    def __init__(self) -> None:
        self._processor = FibersProcessor()
        super().__init__(title="Fibers")

    def _build(self) -> None:
        self.port_out = self.add_port(PortType.OUTPUT, "Output")

        self.add_field(
            FieldDefinition(
                name="scale",
                label="Scale",
                field_type=FieldType.FLOAT,
                default=64.0,
                min_value=2.0,
                max_value=1024.0,
            )
        )
        self.add_field(
            FieldDefinition(
                name="octaves",
                label="Octaves",
                field_type=FieldType.INT,
                default=4,
                min_value=1,
                max_value=8,
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
                name="distortion",
                label="Distortion",
                field_type=FieldType.FLOAT,
                default=2.0,
                min_value=0.0,
                max_value=20.0,
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
        self._processor.scale = self.get_field_value("scale")
        self._processor.octaves = self.get_field_value("octaves")
        self._processor.direction = self.get_field_value("direction")
        self._processor.distortion = self.get_field_value("distortion")
        self._processor.seed = self.get_field_value("seed")
        return self._processor.process(inputs)
