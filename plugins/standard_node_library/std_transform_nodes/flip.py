from typing import Optional

import cv2
import numpy

from catena import api
from std_transform_nodes import IMAGE_NODE_COLOR

_FLIP_CODES = {"Horizontal": 1, "Vertical": 0, "Both": -1}


class FlipNode(api.CatenaNode):
    """A node that flips an input modifier horizontally, vertically, or both."""

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:

        super().__init__(title="Flip")

    def _build(self) -> None:
        self.port_in = self.add_port(api.PortType.INPUT, "Input")
        self.port_out = self.add_port(api.PortType.OUTPUT, "Output")

        self.add_field(
            api.FieldDefinition(
                name="direction",
                label="Direction",
                field_type=api.FieldType.CHOICE,
                default="Horizontal",
                options=["Horizontal", "Vertical", "Both"],
            )
        )

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        """
        Flip an input modifier horizontally, vertically, or both.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Expects key "Input"
                containing a float32 modifier.
        Returns:
            numpy.ndarray | None: The flipped float32 modifier.
        """
        direction = self.get_field_value("direction")

        image = inputs.get("Input")
        if image is None:
            return None

        return cv2.flip(image, _FLIP_CODES[direction]).astype(numpy.float32)
