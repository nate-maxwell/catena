from typing import Callable
from typing import Optional

import numpy

from catena import api
from std_generate_nodes.generator import GeneratorNode

_SHAPES = ["Square", "Circle", "Paraboloid", "Bell", "Gaussian", "Thorn", "Pyramid"]
_GENERATOR = Callable[[numpy.ndarray, numpy.ndarray, float], numpy.ndarray]


class ShapeNode(GeneratorNode):
    """A node that generates a parametric shape mask."""

    def __init__(self) -> None:
        super().__init__(title="Shape")

    def _build(self) -> None:
        self.port_out = self.add_port(api.PortType.OUTPUT, "Output")

        self.add_field(
            api.FieldDefinition(
                name="shape",
                label="Shape",
                field_type=api.FieldType.CHOICE,
                default="Circle",
                options=_SHAPES,
            )
        )
        self.add_field(
            api.FieldDefinition(
                name="size",
                label="Size",
                field_type=api.FieldType.FLOAT,
                default=0.5,
                min_value=0.01,
                max_value=1.0,
            )
        )
        self.add_field(
            api.FieldDefinition(
                name="rotation",
                label="Rotation",
                field_type=api.FieldType.FLOAT,
                default=0.0,
                min_value=-360.0,
                max_value=360.0,
            )
        )

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        """
        Generate a parametric shape mask.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Unused; generators
                produce output from parameters only.
        Returns:
            numpy.ndarray | None: A float32 mask modifier of shape (width, height, 3)
                with values in [0, 1].
        """
        shape = self.get_field_value("shape")
        size = self.get_field_value("size")
        rotation = self.get_field_value("rotation")
        width, height = api.get_texture_resolution()

        cx, cy = width / 2.0, height / 2.0
        y_idx, x_idx = numpy.indices((height, width), dtype=numpy.float32)

        radians = numpy.deg2rad(rotation)
        cos_r = numpy.cos(radians)
        sin_r = numpy.sin(radians)

        dx = x_idx - cx
        dy = y_idx - cy

        rx = dx * cos_r + dy * sin_r
        ry = -dx * sin_r + dy * cos_r

        scale = min(width, height) / 2.0 * size

        generators: dict[str, _GENERATOR] = {
            "Square": self._generate_square,
            "Circle": self._generate_circle,
            "Paraboloid": self._generate_paraboloid,
            "Bell": self._generate_bell,
            "Gaussian": self._generate_gaussian,
            "Thorn": self._generate_thorn,
            "Pyramid": self._generate_pyramid,
        }

        generator = generators.get(shape, self._generate_circle)
        result = numpy.clip(generator(rx, ry, scale), 0.0, 1.0)
        return numpy.repeat(result[:, :, None], 4, axis=2).astype(numpy.float32)

    @staticmethod
    def _generate_square(
        rx: numpy.ndarray, ry: numpy.ndarray, scale: float
    ) -> numpy.ndarray:
        mask = (numpy.abs(rx) <= scale) & (numpy.abs(ry) <= scale)
        return mask.astype(numpy.float32)

    @staticmethod
    def _generate_circle(
        rx: numpy.ndarray, ry: numpy.ndarray, scale: float
    ) -> numpy.ndarray:
        dist = numpy.sqrt(rx * rx + ry * ry)
        return (dist <= scale).astype(numpy.float32)

    @staticmethod
    def _generate_paraboloid(
        rx: numpy.ndarray, ry: numpy.ndarray, scale: float
    ) -> numpy.ndarray:
        dist_sq = (rx * rx + ry * ry) / (scale * scale)
        return numpy.clip(1.0 - dist_sq, 0.0, 1.0)

    @staticmethod
    def _generate_bell(
        rx: numpy.ndarray, ry: numpy.ndarray, scale: float
    ) -> numpy.ndarray:
        dist = numpy.sqrt(rx * rx + ry * ry) / scale
        return numpy.clip(numpy.cos(dist * numpy.pi / 2.0), 0.0, 1.0)

    @staticmethod
    def _generate_gaussian(
        rx: numpy.ndarray, ry: numpy.ndarray, scale: float
    ) -> numpy.ndarray:
        dist_sq = (rx * rx + ry * ry) / (scale * scale)
        return numpy.exp(-dist_sq * 2.0)

    @staticmethod
    def _generate_thorn(
        rx: numpy.ndarray, ry: numpy.ndarray, scale: float
    ) -> numpy.ndarray:
        dist = numpy.sqrt(rx * rx + ry * ry) / scale
        return numpy.clip(1.0 - dist, 0.0, 1.0) ** 4

    @staticmethod
    def _generate_pyramid(
        rx: numpy.ndarray, ry: numpy.ndarray, scale: float
    ) -> numpy.ndarray:
        dist = numpy.maximum(numpy.abs(rx), numpy.abs(ry)) / scale
        return numpy.clip(1.0 - dist, 0.0, 1.0)
