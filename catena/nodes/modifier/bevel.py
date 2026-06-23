from typing import Optional

import cv2
import numpy
from PySide6TK.Nodes import FieldDefinition
from PySide6TK.Nodes import FieldType
from PySide6TK.Nodes import PortType

from catena.nodes.node_gui import CatenaNode
from catena.nodes.modifier import IMAGE_NODE_COLOR
from catena.nodes.node_processor import ProcessorNode


class BevelProcessor(ProcessorNode):
    """A headless processor that adds a beveled edge to a shape mask."""

    def __init__(
        self,
        distance: float = 10.0,
        depth: float = 1.0,
        soft: bool = True,
    ) -> None:
        super().__init__()
        self.distance = distance
        self.depth = depth
        self.soft = soft

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        """
        Generate a height-map bevel from a shape mask.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Expects key "Input"
                containing a float32 shape mask.
        Returns:
            numpy.ndarray | None: A float32 height map of shape (H, W, 3)
                with values in [0, 1]. Background is black, shape interior
                is white, with a beveled transition at the boundary.
        """
        image = inputs.get("Input")
        if image is None:
            return None

        if image.ndim == 3:
            gray = image.mean(axis=2)
        else:
            gray = image

        mask = (gray > 0.5).astype(numpy.uint8) * 255

        corner_radius = max(1, int(self.distance * 0.6))
        kernel_size = corner_radius * 2 + 1
        kernel = cv2.getStructuringElement(
            cv2.MORPH_ELLIPSE, (kernel_size, kernel_size)
        )

        mask_rounded = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask_rounded = cv2.morphologyEx(mask_rounded, cv2.MORPH_CLOSE, kernel)

        dist_inside = cv2.distanceTransform(mask_rounded, cv2.DIST_L2, 5)
        dist_outside = cv2.distanceTransform(255 - mask_rounded, cv2.DIST_L2, 5)

        signed_dist = (dist_inside - dist_outside) * self.depth

        if self.soft:
            height_field = numpy.tanh(signed_dist / self.distance)
        else:
            height_field = numpy.clip(signed_dist / self.distance, -1.0, 1.0)

        height_field = (height_field + 1.0) * 0.5

        return numpy.repeat(height_field[:, :, None], 3, axis=2).astype(numpy.float32)


class BevelNode(CatenaNode):
    """A node that adds a beveled highlight/shadow edge to a shape mask."""

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        self._processor = BevelProcessor()
        super().__init__(title="Bevel")

    def _build(self) -> None:
        self.port_in = self.add_port(PortType.INPUT, "Input")
        self.port_out = self.add_port(PortType.OUTPUT, "Output")

        self.add_field(
            FieldDefinition(
                name="distance",
                label="Distance",
                field_type=FieldType.FLOAT,
                default=10.0,
                min_value=1.0,
                max_value=100.0,
            )
        )
        self.add_field(
            FieldDefinition(
                name="depth",
                label="Depth",
                field_type=FieldType.FLOAT,
                default=1.0,
                min_value=-5.0,
                max_value=5.0,
            )
        )
        self.add_field(
            FieldDefinition(
                name="soft",
                label="Soft",
                field_type=FieldType.BOOL,
                default=True,
            )
        )

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        self._processor.distance = self.get_field_value("distance")
        self._processor.depth = self.get_field_value("depth")
        self._processor.soft = self.get_field_value("soft")
        return self._processor.process(inputs)
