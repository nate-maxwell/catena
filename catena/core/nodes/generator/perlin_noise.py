from typing import Optional

import numpy
from PySide6TK.Nodes.node import FieldDefinition
from PySide6TK.Nodes.node import FieldType
from PySide6TK.Nodes.node import PortType

from catena.core.nodes.base import CatenaNode
from catena.core.nodes.generator import IMAGE_NODE_COLOR


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


class PerlinNoiseNode(CatenaNode):
    """A node that generates Perlin-style value noise."""

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        super().__init__(title="Perlin Noise", body_height=80)

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
        scale = self.get_field_value("scale")
        octaves = self.get_field_value("octaves")
        seed = self.get_field_value("seed")

        width, height = 512, 512
        total = numpy.zeros((height, width), dtype=numpy.float32)
        amplitude = 1.0
        max_amplitude = 0.0
        current_scale = scale

        for i in range(octaves):
            total += _value_noise((height, width), current_scale, seed + i) * amplitude
            max_amplitude += amplitude
            amplitude *= 0.5
            current_scale *= 0.5
            current_scale = max(current_scale, 2.0)

        total /= max_amplitude
        result = numpy.repeat(total[:, :, None], 3, axis=2).astype(numpy.float32)
        return result
