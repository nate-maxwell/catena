from typing import Optional

import cv2
import numpy

from catena import api
from std_generate_nodes.generator import GeneratorNode


class DirectionalNoiseNode(GeneratorNode):
    """A node that generates directional streaked noise."""

    def __init__(self) -> None:
        super().__init__(title="Directional Noise")

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
                name="angle",
                label="Angle",
                field_type=api.FieldType.FLOAT,
                default=0.0,
                min_value=-360.0,
                max_value=360.0,
            )
        )
        self.add_field(
            api.FieldDefinition(
                name="angle_random",
                label="Angle Random",
                field_type=api.FieldType.FLOAT,
                default=0.0,
                min_value=0.0,
                max_value=1.0,
            )
        )
        self.add_field(
            api.FieldDefinition(
                name="disorder",
                label="Disorder",
                field_type=api.FieldType.FLOAT,
                default=0.5,
                min_value=0.0,
                max_value=1.0,
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

    def _value_noise(
        self,
        height: int,
        width: int,
        scale: float,
        rng: numpy.random.Generator,
    ) -> numpy.ndarray:
        grid_h = max(2, int(round(height / scale)))
        grid_w = max(2, int(round(width / scale)))
        lattice = rng.random((grid_h, grid_w)).astype(numpy.float32)

        ys = numpy.linspace(0, grid_h, height, endpoint=False)
        xs = numpy.linspace(0, grid_w, width, endpoint=False)

        y0 = numpy.floor(ys).astype(int) % grid_h
        x0 = numpy.floor(xs).astype(int) % grid_w
        y1 = (y0 + 1) % grid_h
        x1 = (x0 + 1) % grid_w

        fy = (ys - numpy.floor(ys))[:, None]
        fx = (xs - numpy.floor(xs))[None, :]

        sy = fy * fy * (3 - 2 * fy)
        sx = fx * fx * (3 - 2 * fx)

        tl = lattice[numpy.ix_(y0, x0)]
        tr = lattice[numpy.ix_(y0, x1)]
        bl = lattice[numpy.ix_(y1, x0)]
        br = lattice[numpy.ix_(y1, x1)]

        return (
            tl * (1 - sx) * (1 - sy)
            + tr * sx * (1 - sy)
            + bl * (1 - sx) * sy
            + br * sx * sy
        )

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        """
        Generate directional streaked noise similar to Photoshop's fiber effect
        with per-column angle variation and noise-based streak warping.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Unused; generators
                produce output from parameters only.
        Returns:
            numpy.ndarray | None: A float32 directional noise modifier with
                values in [0, 1].
        """
        scale = self.get_field_value("scale")
        angle = self.get_field_value("angle")
        angle_random = self.get_field_value("angle_random")
        disorder = self.get_field_value("disorder")
        seed = self.get_field_value("seed")
        seed = int(seed * 255) if isinstance(seed, float) else int(seed)
        width, height = api.get_texture_resolution()
        rng = numpy.random.default_rng(seed)

        fiber_length_min = max(1, int(scale * 0.5))
        fiber_length_max = max(2, int(scale * 2.0))

        fibers = numpy.zeros((height, width), dtype=numpy.float32)
        for x in range(width):
            column = numpy.zeros(height, dtype=numpy.float32)
            y = 0
            while y < height:
                length = int(rng.uniform(fiber_length_min, fiber_length_max))
                value = rng.random()
                end = min(y + length, height)
                column[y:end] = value
                y = end
            fibers[:, x] = column

        if disorder > 0.0:
            disorder_noise = self._value_noise(height, width, max(scale, 4), rng)
            y_idx, x_idx = numpy.indices((height, width), dtype=numpy.float32)
            map_y = (y_idx + (disorder_noise - 0.5) * disorder * scale).astype(
                numpy.float32
            )
            map_x = x_idx.astype(numpy.float32)
            fibers = cv2.remap(
                fibers, map_x, map_y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT
            )

        if angle != 0.0:
            center = (width / 2.0, height / 2.0)
            matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
            fibers = cv2.warpAffine(
                fibers, matrix, (width, height), borderMode=cv2.BORDER_WRAP
            )

        if angle_random > 0.0:
            angle_noise = self._value_noise(height, width, max(scale * 4, 8), rng)
            angle_offsets = (angle_noise - 0.5) * angle_random * 180.0
            y_idx, x_idx = numpy.indices((height, width), dtype=numpy.float32)
            radians = numpy.deg2rad(angle_offsets)
            map_x = (x_idx + numpy.sin(radians) * scale * 0.5).astype(numpy.float32)
            map_y = (y_idx + numpy.cos(radians) * scale * 0.5).astype(numpy.float32)
            fibers = cv2.remap(
                fibers, map_x, map_y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT
            )

        fibers -= fibers.min()
        if fibers.max() > 0:
            fibers /= fibers.max()

        return numpy.repeat(fibers[:, :, None], 4, axis=2).astype(numpy.float32)
