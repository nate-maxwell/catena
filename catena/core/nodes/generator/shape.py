from typing import Callable
from typing import Optional

import numpy
from PySide6TK.Nodes.node import FieldDefinition
from PySide6TK.Nodes.node import FieldType
from PySide6TK.Nodes.node import PortType

from catena.core.nodes.base import CatenaNode
from catena.core.nodes.generator import IMAGE_NODE_COLOR

_SHAPES = ["Square", "Circle", "Paraboloid", "Bell", "Gaussian", "Thorn", "Pyramid"]
_GENERATOR = Callable[[numpy.ndarray, numpy.ndarray, float], numpy.ndarray]


class ShapeNode(CatenaNode):
    """A node that generates a parametric shape mask."""

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        super().__init__(title="Shape", body_height=80)

    def _build(self) -> None:
        self.port_out = self.add_port(PortType.OUTPUT, "Output")

        self.add_field(
            FieldDefinition(
                name="shape",
                label="Shape",
                field_type=FieldType.CHOICE,
                default="Circle",
                options=_SHAPES,
            )
        )
        self.add_field(
            FieldDefinition(
                name="size",
                label="Size",
                field_type=FieldType.FLOAT,
                default=0.5,
                min_value=0.01,
                max_value=1.0,
            )
        )
        self.add_field(
            FieldDefinition(
                name="rotation",
                label="Rotation",
                field_type=FieldType.FLOAT,
                default=0.0,
                min_value=-360.0,
                max_value=360.0,
            )
        )

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        shape = self.get_field_value("shape")
        size = self.get_field_value("size")
        rotation = self.get_field_value("rotation")

        width, height = 512, 512

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
        result = generator(rx, ry, scale)

        result = numpy.clip(result, 0.0, 1.0)
        return numpy.repeat(result[:, :, None], 3, axis=2).astype(numpy.float32)

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
        mask = dist <= scale
        return mask.astype(numpy.float32)

    @staticmethod
    def _generate_paraboloid(
        rx: numpy.ndarray, ry: numpy.ndarray, scale: float
    ) -> numpy.ndarray:
        dist_sq = (rx * rx + ry * ry) / (scale * scale)
        result = 1.0 - dist_sq
        return numpy.clip(result, 0.0, 1.0)

    @staticmethod
    def _generate_bell(
        rx: numpy.ndarray, ry: numpy.ndarray, scale: float
    ) -> numpy.ndarray:
        dist = numpy.sqrt(rx * rx + ry * ry) / scale
        result = numpy.cos(dist * numpy.pi / 2.0)
        return numpy.clip(result, 0.0, 1.0)

    @staticmethod
    def _generate_gaussian(
        rx: numpy.ndarray, ry: numpy.ndarray, scale: float
    ) -> numpy.ndarray:
        dist_sq = (rx * rx + ry * ry) / (scale * scale)
        result = numpy.exp(-dist_sq * 2.0)
        return result

    @staticmethod
    def _generate_thorn(
        rx: numpy.ndarray, ry: numpy.ndarray, scale: float
    ) -> numpy.ndarray:
        dist = numpy.sqrt(rx * rx + ry * ry) / scale
        result = 1.0 - dist
        result = numpy.clip(result, 0.0, 1.0)
        result = result**4
        return result

    @staticmethod
    def _generate_pyramid(
        rx: numpy.ndarray, ry: numpy.ndarray, scale: float
    ) -> numpy.ndarray:
        dist = numpy.maximum(numpy.abs(rx), numpy.abs(ry)) / scale
        result = 1.0 - dist
        return numpy.clip(result, 0.0, 1.0)
