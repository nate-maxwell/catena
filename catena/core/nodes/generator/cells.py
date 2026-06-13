from typing import Optional

import cv2
import numpy
from PySide6TK.Nodes.node import FieldDefinition
from PySide6TK.Nodes.node import FieldType
from PySide6TK.Nodes.node import PortType

from catena.core.nodes.base import CatenaNode
from catena.core.nodes.generator import IMAGE_NODE_COLOR


class CellsNode(CatenaNode):
    """A node that generates cellular (Worley) noise."""

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        super().__init__(title="Cells", width=180, body_height=80)

    def _build(self) -> None:
        self.port_out = self.add_port(PortType.OUTPUT, "Output")

        self.add_field(
            FieldDefinition(
                name="cells",
                label="Cells",
                field_type=FieldType.INT,
                default=16,
                min_value=2,
                max_value=128,
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
        self.add_field(
            FieldDefinition(
                name="invert",
                label="Invert",
                field_type=FieldType.BOOL,
                default=False,
            )
        )

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        cells = self.get_field_value("cells")
        seed = self.get_field_value("seed")
        invert = self.get_field_value("invert")

        width, height = 512, 512
        rng = numpy.random.default_rng(seed)

        points = rng.random((cells, 2))
        points[:, 0] *= width
        points[:, 1] *= height

        y_idx, x_idx = numpy.indices((height, width)).astype(numpy.float32)

        min_dist = numpy.full((height, width), numpy.inf, dtype=numpy.float32)

        for px, py in points:
            dx = x_idx - px
            dy = y_idx - py
            dist = numpy.sqrt(dx * dx + dy * dy)
            min_dist = numpy.minimum(min_dist, dist)

        min_dist /= min_dist.max()

        if invert:
            min_dist = 1.0 - min_dist

        gray = (min_dist * 255.0).astype(numpy.uint8)
        result = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        return result
