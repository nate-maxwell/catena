from typing import Optional

import cv2
import numpy
from PySide6TK.Nodes import FieldDefinition
from PySide6TK.Nodes import FieldType
from PySide6TK.Nodes import PortType

from catena.nodes.node_gui import CatenaNode
from catena.nodes.node_processor import ProcessorNode
from catena.nodes.transform import IMAGE_NODE_COLOR


class TileProcessor(ProcessorNode):
    """A headless processor that repeats an input image across a grid."""

    def __init__(self, tiles_x: int = 2, tiles_y: int = 2) -> None:
        super().__init__()
        self.tiles_x = tiles_x
        self.tiles_y = tiles_y

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        """
        Repeat an input image across a grid of tiles.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Expects key "Input"
                containing a float32 image.
        Returns:
            numpy.ndarray | None: A float32 image of the same size as the
                input with the content tiled across a grid.
        """
        image = inputs.get("Input")
        if image is None:
            return None

        height, width = image.shape[:2]

        tile_width = max(1, width // self.tiles_x)
        tile_height = max(1, height // self.tiles_y)

        small = cv2.resize(image, (tile_width, tile_height))
        tiled = numpy.tile(small, (self.tiles_y, self.tiles_x, 1))

        return cv2.resize(tiled, (width, height)).astype(numpy.float32)


class TileNode(CatenaNode):
    """A node that repeats an input image across a grid."""

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        self._processor = TileProcessor()
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
        self._processor.tiles_x = self.get_field_value("tiles_x")
        self._processor.tiles_y = self.get_field_value("tiles_y")
        return self._processor.process(inputs)
