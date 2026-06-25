from typing import Optional

import numpy
from PySide6TK.Nodes.node import FieldDefinition
from PySide6TK.Nodes.node import FieldType
from PySide6TK.Nodes.node import PortType

from catena.nodes.generate import IMAGE_NODE_COLOR
from catena.nodes.generate.generator import GeneratorNode
from catena.nodes.node_processor import ProcessorNode
from catena.preferences import preferences


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


class PerlinNoiseProcessor(ProcessorNode):
    """A headless processor that generates Perlin-style value noise."""

    def __init__(
        self,
        scale: float = 64.0,
        octaves: int = 4,
        seed: int = 0,
    ) -> None:
        super().__init__()
        self.scale = scale
        self.octaves = octaves
        self.seed = seed

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]] | None = None
    ) -> Optional[numpy.ndarray]:
        """
        Generate Perlin-style value noise.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Unused; generators
                produce output from parameters only.
        Returns:
            numpy.ndarray | None: A float32 grayscale noise modifier of shape
                (width, height, 3) with values in [0, 1].
        """
        width = preferences.Preferences().general_preferences.texture_resolution
        height = width
        total = numpy.zeros((height, width), dtype=numpy.float32)
        amplitude = 1.0
        max_amplitude = 0.0
        current_scale = self.scale

        for i in range(self.octaves):
            total += (
                _value_noise((height, width), current_scale, self.seed + i) * amplitude
            )
            max_amplitude += amplitude
            amplitude *= 0.5
            current_scale *= 0.5
            current_scale = max(current_scale, 2.0)

        total /= max_amplitude
        return numpy.repeat(total[:, :, None], 4, axis=2).astype(numpy.float32)


class PerlinNoiseNode(GeneratorNode):
    """A node that generates Perlin-style value noise."""

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        self._processor = PerlinNoiseProcessor()
        super().__init__(title="Perlin Noise")

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

        seed = self.get_field_value("seed")
        self._processor.seed = int(seed * 255) if isinstance(seed, float) else int(seed)

        return self._processor.process(inputs)
