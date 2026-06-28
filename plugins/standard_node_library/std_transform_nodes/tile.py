from typing import Optional

import cv2
import numpy

from catena import api
from std_transform_nodes import IMAGE_NODE_COLOR


class TileNode(api.CatenaNode):
    """A node that repeats an input modifier across a grid."""

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:

        super().__init__(title="Tile")

    def _build(self) -> None:
        self.port_in = self.add_port(api.PortType.INPUT, "Input")
        self.port_out = self.add_port(api.PortType.OUTPUT, "Output")

        self.add_field(
            api.FieldDefinition(
                name="tiles_x",
                label="Tiles X",
                field_type=api.FieldType.INT,
                default=2,
                min_value=1,
                max_value=64,
            )
        )
        self.add_field(
            api.FieldDefinition(
                name="tiles_y",
                label="Tiles Y",
                field_type=api.FieldType.INT,
                default=2,
                min_value=1,
                max_value=64,
            )
        )

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        """
        Repeat an input modifier across a grid of tiles.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Expects key "Input"
                containing a float32 modifier.
        Returns:
            numpy.ndarray | None: A float32 modifier of the same size as the
                input with the content tiled across a grid.
        """
        tiles_x = self.get_field_value("tiles_x")
        tiles_y = self.get_field_value("tiles_y")

        image = inputs.get("Input")
        if image is None:
            return None

        height, width = image.shape[:2]

        tile_width = max(1, width // tiles_x)
        tile_height = max(1, height // tiles_y)

        small = cv2.resize(image, (tile_width, tile_height))
        tiled = numpy.tile(small, (tiles_y, tiles_x, 1))

        return cv2.resize(tiled, (width, height)).astype(numpy.float32)
