from typing import Optional

import numpy

from catena import api
from std_generate_nodes.generator import GeneratorNode


def _fade(t: numpy.ndarray) -> numpy.ndarray:
    return t * t * t * (t * (t * 6.0 - 15.0) + 10.0)


def _perlin_noise(shape: tuple[int, int], scale: float, seed: int) -> numpy.ndarray:
    height, width = shape
    rng = numpy.random.default_rng(seed)

    grid_h = max(2, int(round(height / scale)))
    grid_w = max(2, int(round(width / scale)))
    gradients = rng.random((grid_h, grid_w, 2), dtype=numpy.float32) * 2.0 - 1.0
    norms = numpy.linalg.norm(gradients, axis=2, keepdims=True)
    gradients = gradients / numpy.maximum(norms, 1e-8)

    ys = numpy.linspace(0, grid_h, height, endpoint=False, dtype=numpy.float32)
    xs = numpy.linspace(0, grid_w, width, endpoint=False, dtype=numpy.float32)

    y0 = numpy.floor(ys).astype(int) % grid_h
    x0 = numpy.floor(xs).astype(int) % grid_w
    y1 = (y0 + 1) % grid_h
    x1 = (x0 + 1) % grid_w

    fy = (ys - numpy.floor(ys))[:, None]
    fx = (xs - numpy.floor(xs))[None, :]

    u = _fade(fx)
    v = _fade(fy)

    top_left = gradients[numpy.ix_(y0, x0)]
    top_right = gradients[numpy.ix_(y0, x1)]
    bottom_left = gradients[numpy.ix_(y1, x0)]
    bottom_right = gradients[numpy.ix_(y1, x1)]

    dot_top_left = top_left[..., 0] * fx + top_left[..., 1] * fy
    dot_top_right = top_right[..., 0] * (fx - 1.0) + top_right[..., 1] * fy
    dot_bottom_left = bottom_left[..., 0] * fx + bottom_left[..., 1] * (fy - 1.0)
    dot_bottom_right = (
        bottom_right[..., 0] * (fx - 1.0) + bottom_right[..., 1] * (fy - 1.0)
    )

    top = dot_top_left * (1.0 - u) + dot_top_right * u
    bottom = dot_bottom_left * (1.0 - u) + dot_bottom_right * u
    result = top * (1.0 - v) + bottom * v

    return result.astype(numpy.float32)


class PerlinNoiseNode(GeneratorNode):
    """A node that generates gradient-based Perlin noise."""

    def __init__(self) -> None:
        super().__init__(title="Perlin Noise")

    def _build(self) -> None:
        self.port_out = self.add_port(api.PortType.OUTPUT, "Output")

        self.add_field(
            api.FieldDefinition(
                name="scale",
                label="Scale",
                field_type=api.FieldType.FLOAT,
                default=64.0,
                min_value=2.0,
                max_value=1024.0,
            )
        )
        self.add_field(
            api.FieldDefinition(
                name="octaves",
                label="Octaves",
                field_type=api.FieldType.INT,
                default=4,
                min_value=1,
                max_value=8,
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
        Generate gradient-based Perlin noise.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Unused; generators
                produce output from parameters only.
        Returns:
            numpy.ndarray | None: A float32 grayscale noise modifier of shape
                (height, width, 4) with values in [0, 1].
        """
        scale = self.get_field_value("scale")
        octaves = self.get_field_value("octaves")
        seed = self.get_field_value("seed")
        seed = int(seed * 255) if isinstance(seed, float) else int(seed)
        width, height = api.get_texture_resolution()
        total = numpy.zeros((height, width), dtype=numpy.float32)
        amplitude = 1.0
        max_amplitude = 0.0

        current_scale = scale
        for i in range(octaves):
            total += _perlin_noise((height, width), current_scale, seed + i) * amplitude
            max_amplitude += amplitude
            amplitude *= 0.5
            current_scale = max(current_scale * 0.5, 2.0)

        total /= max_amplitude
        total -= total.min()
        if total.max() > 0:
            total /= total.max()

        return numpy.repeat(total[:, :, None], 4, axis=2).astype(numpy.float32)
