from typing import Optional

import cv2
import numpy
from PySide6TK.Nodes.node import FieldDefinition
from PySide6TK.Nodes.node import FieldType
from PySide6TK.Nodes.node import PortType

from catena.core.nodes.base import CatenaNode
from catena.core.nodes.transform import IMAGE_NODE_COLOR


class TileNode(CatenaNode):
    """A node that repeats an input image across a grid."""

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        super().__init__(title="Tile")

    def _build(self) -> None:
        self.port_in = self.add_port(PortType.INPUT, "Input")
        self.port_out = self.add_port(PortType.OUTPUT, "Output")

        self.add_field(
            FieldDefinition(
                name="tiles_x",
                label="Tiles X",
                field_type=FieldType.INT,
                default=2,
                min_value=1,
                max_value=64,
            )
        )
        self.add_field(
            FieldDefinition(
                name="tiles_y",
                label="Tiles Y",
                field_type=FieldType.INT,
                default=2,
                min_value=1,
                max_value=64,
            )
        )

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        image = inputs.get("Input")
        if image is None:
            return None

        tiles_x = self.get_field_value("tiles_x")
        tiles_y = self.get_field_value("tiles_y")

        height, width = image.shape[:2]

        tile_width = max(1, width // tiles_x)
        tile_height = max(1, height // tiles_y)

        small = cv2.resize(image, (tile_width, tile_height))
        tiled = numpy.tile(small, (tiles_y, tiles_x, 1))

        result = cv2.resize(tiled, (width, height))
        return result.astype(numpy.float32)
