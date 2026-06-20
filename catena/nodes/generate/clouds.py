from typing import Optional

import numpy
from PySide6TK.Nodes import FieldDefinition
from PySide6TK.Nodes import FieldType
from PySide6TK.Nodes import PortType

from catena.nodes.generate.generator import GeneratorNode
from catena.nodes.node_processor import ProcessorNode


def _value_noise(shape: tuple[int, int], scale: float, seed: int) -> numpy.ndarray:
    height, width = shape
    rng = numpy.random.default_rng(seed)

    grid_h = max(2, int(round(height / scale)))
    grid_w = max(2, int(round(width / scale)))
    lattice = rng.random((grid_h, grid_w))

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

    sy = smooth(fy)
    sx = smooth(fx)

    top_left = lattice[numpy.ix_(y0, x0)]
    top_right = lattice[numpy.ix_(y0, x1)]
    bottom_left = lattice[numpy.ix_(y1, x0)]
    bottom_right = lattice[numpy.ix_(y1, x1)]

    top = top_left * (1 - sx) + top_right * sx
    bottom = bottom_left * (1 - sx) + bottom_right * sx
    result = top * (1 - sy) + bottom * sy

    return result


class CloudsProcessor(ProcessorNode):
    """A headless processor that generates soft cloud-like noise."""

    def __init__(
        self,
        scale: float = 128.0,
        octaves: int = 5,
        persistence: float = 0.6,
        contrast: float = 1.5,
        seed: int = 0,
    ) -> None:
        super().__init__()
        self.scale = scale
        self.octaves = octaves
        self.persistence = persistence
        self.contrast = contrast
        self.seed = seed

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        """
        Generate soft cloud-like multi-octave value noise.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Unused; generators
                produce output from parameters only.
        Returns:
            numpy.ndarray | None: A float32 cloud noise image of shape
                (512, 512, 3) with values in [0, 1].
        """
        width, height = 512, 512
        total = numpy.zeros((height, width), dtype=numpy.float32)
        amplitude = 1.0
        max_amplitude = 0.0
        current_scale = self.scale

        for i in range(self.octaves):
            total += (
                _value_noise((height, width), current_scale, self.seed + i) * amplitude
            )
            max_amplitude += amplitude
            amplitude *= self.persistence
            current_scale *= 0.5
            current_scale = max(current_scale, 2.0)

        total /= max_amplitude
        total = numpy.clip((total - 0.5) * self.contrast + 0.5, 0.0, 1.0)

        return numpy.repeat(total[:, :, None], 3, axis=2).astype(numpy.float32)


class CloudsNode(GeneratorNode):
    """A node that generates soft cloud-like noise."""

    def __init__(self) -> None:
        self._processor = CloudsProcessor()
        super().__init__(title="Clouds")

    def _build(self) -> None:
        self.port_out = self.add_port(PortType.OUTPUT, "Output")

        self.add_field(
            FieldDefinition(
                name="scale",
                label="Scale",
                field_type=FieldType.FLOAT,
                default=128.0,
                min_value=4.0,
                max_value=1024.0,
            )
        )
        self.add_field(
            FieldDefinition(
                name="octaves",
                label="Octaves",
                field_type=FieldType.INT,
                default=5,
                min_value=1,
                max_value=8,
            )
        )
        self.add_field(
            FieldDefinition(
                name="persistence",
                label="Persistence",
                field_type=FieldType.FLOAT,
                default=0.6,
                min_value=0.1,
                max_value=1.0,
            )
        )
        self.add_field(
            FieldDefinition(
                name="contrast",
                label="Contrast",
                field_type=FieldType.FLOAT,
                default=1.5,
                min_value=0.1,
                max_value=5.0,
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
        self._processor.persistence = self.get_field_value("persistence")
        self._processor.contrast = self.get_field_value("contrast")
        self._processor.seed = self.get_field_value("seed")
        return self._processor.process(inputs)
