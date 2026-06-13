from typing import Optional

import cv2
import numpy
from PySide6 import QtGui
from PySide6TK.Nodes.node import FieldDefinition
from PySide6TK.Nodes.node import FieldType
from PySide6TK.Nodes.node import PortType

from catena.core.nodes.base import CatenaNode
from catena.core.nodes.generator import IMAGE_NODE_COLOR


def _value_noise(shape: tuple[int, int], scale: float, seed: int) -> numpy.ndarray:
    height, width = shape
    rng = numpy.random.default_rng(seed)

    grid_h = max(2, int(height / scale) + 2)
    grid_w = max(2, int(width / scale) + 2)
    lattice = rng.random((grid_h, grid_w))

    ys = numpy.linspace(0, grid_h - 1.0001, height)
    xs = numpy.linspace(0, grid_w - 1.0001, width)

    y0 = numpy.floor(ys).astype(int)
    x0 = numpy.floor(xs).astype(int)
    y1 = y0 + 1
    x1 = x0 + 1

    fy = (ys - y0)[:, None]
    fx = (xs - x0)[None, :]

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


class CloudsNode(CatenaNode):
    """A node that generates soft cloud-like noise."""

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        super().__init__(title="Clouds", width=180, body_height=100)

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
        scale = self.get_field_value("scale")
        octaves = self.get_field_value("octaves")
        persistence = self.get_field_value("persistence")
        contrast = self.get_field_value("contrast")
        seed = self.get_field_value("seed")

        width, height = 512, 512
        total = numpy.zeros((height, width), dtype=numpy.float32)
        amplitude = 1.0
        max_amplitude = 0.0
        current_scale = scale

        for i in range(octaves):
            total += _value_noise((height, width), current_scale, seed + i) * amplitude
            max_amplitude += amplitude
            amplitude *= persistence
            current_scale *= 0.5
            current_scale = max(current_scale, 2.0)

        total /= max_amplitude

        total = numpy.clip((total - 0.5) * contrast + 0.5, 0.0, 1.0)

        gray = (total * 255.0).astype(numpy.uint8)
        result = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        return result
