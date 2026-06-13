from typing import Optional

import cv2
import numpy
from PySide6TK.Nodes.node import FieldDefinition
from PySide6TK.Nodes.node import FieldType
from PySide6TK.Nodes.node import PortType

from catena.core.nodes.base import CatenaNode
from catena.core.nodes.generator import IMAGE_NODE_COLOR


class BNWSpotsNode(CatenaNode):
    """A node that generates random black and white spots."""

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        super().__init__(title="BnW Spots", body_height=80)

    def _build(self) -> None:
        self.port_out = self.add_port(PortType.OUTPUT, "Output")

        self.add_field(
            FieldDefinition(
                name="density",
                label="Density",
                field_type=FieldType.FLOAT,
                default=0.01,
                min_value=0.0001,
                max_value=100,
            )
        )
        self.add_field(
            FieldDefinition(
                name="size",
                label="Size",
                field_type=FieldType.INT,
                default=4,
                min_value=1,
                max_value=64,
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
        density = self.get_field_value("density")
        size = self.get_field_value("size")
        seed = self.get_field_value("seed")

        width, height = 512, 512
        rng = numpy.random.default_rng(seed)

        canvas = numpy.full((height, width), 128, dtype=numpy.uint8)

        num_spots = int(width * height * density)
        xs = rng.integers(0, width, num_spots)
        ys = rng.integers(0, height, num_spots)
        colors = rng.choice([0, 255], num_spots)

        for x, y, color in zip(xs, ys, colors):
            cv2.circle(canvas, (int(x), int(y)), size, int(color), -1)

        result = cv2.cvtColor(canvas, cv2.COLOR_GRAY2BGR)
        return result
