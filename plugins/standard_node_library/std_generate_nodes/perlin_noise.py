from typing import Optional

import numpy

from catena import api
from std_generate_nodes.generator import GeneratorNode


def _fade(t: numpy.ndarray) -> numpy.ndarray:
    return t * t * t * (t * (t * 6.0 - 15.0) + 10.0)


def _tileable_perlin_noise(
    shape: tuple[int, int],
    period_h: int,
    period_w: int,
    seed: int,
    frequency: int = 1,
) -> numpy.ndarray:
    height, width = shape
    rng = numpy.random.default_rng(seed)

    gradients = rng.random((period_h, period_w, 2), dtype=numpy.float32) * 2.0 - 1.0
    norms = numpy.linalg.norm(gradients, axis=2, keepdims=True)
    gradients = gradients / numpy.maximum(norms, 1e-8)

    ys = (numpy.arange(height, dtype=numpy.float32) + 0.5) / height
    xs = (numpy.arange(width, dtype=numpy.float32) + 0.5) / width
    ys *= period_h * frequency
    xs *= period_w * frequency

    y0 = numpy.floor(ys).astype(int) % period_h
    x0 = numpy.floor(xs).astype(int) % period_w
    y1 = (y0 + 1) % period_h
    x1 = (x0 + 1) % period_w

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
    dot_bottom_right = bottom_right[..., 0] * (fx - 1.0) + bottom_right[..., 1] * (
        fy - 1.0
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
        if scale < 1:
            scale = 1
        octaves = self.get_field_value("octaves")
        seed = self.get_field_value("seed")
        seed = int(seed * 255) if isinstance(seed, float) else int(seed)
        width, height = api.get_texture_resolution()
        total = numpy.zeros((height, width), dtype=numpy.float32)
        amplitude = 1.0
        max_amplitude = 0.0

        base_period_h = max(2, int(round(height / scale)))
        base_period_w = max(2, int(round(width / scale)))

        for i in range(octaves):
            frequency = 1 << i
            total += (
                _tileable_perlin_noise(
                    (height, width),
                    base_period_h,
                    base_period_w,
                    seed + i,
                    frequency,
                )
                * amplitude
            )
            max_amplitude += amplitude
            amplitude *= 0.5

        total /= max_amplitude
        total -= total.min()
        if total.max() > 0:
            total /= total.max()

        return numpy.repeat(total[:, :, None], 4, axis=2).astype(numpy.float32)
