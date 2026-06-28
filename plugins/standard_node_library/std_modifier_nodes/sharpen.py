from typing import Optional

import cv2
import numpy

from catena import api
from std_modifier_nodes import IMAGE_NODE_COLOR


class SharpenNode(api.CatenaNode):
    """A node that sharpens an input modifier using an unsharp mask."""

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:

        super().__init__(title="Sharpen")

    def _build(self) -> None:
        self.port_in = self.add_port(api.PortType.INPUT, "Input")
        self.port_out = self.add_port(api.PortType.OUTPUT, "Output")

        self.add_field(
            api.FieldDefinition(
                name="amount",
                label="Amount",
                field_type=api.FieldType.FLOAT,
                default=1.0,
                min_value=0.0,
                max_value=100.0,
            )
        )
        self.add_field(
            api.FieldDefinition(
                name="radius",
                label="Radius",
                field_type=api.FieldType.FLOAT,
                default=2.0,
                min_value=0.1,
                max_value=100.0,
            )
        )

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        """
        Sharpen an input modifier using an unsharp mask.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Expects key "Input"
                containing a float32 modifier.
        Returns:
            numpy.ndarray | None: The sharpened float32 modifier. Values may
                exceed [0, 1] and should be clamped downstream if needed.
        """
        amount = self.get_field_value("amount")
        radius = self.get_field_value("radius")

        image = inputs.get("Input")
        if image is None:
            return None

        if amount <= 0:
            return image

        blurred = cv2.GaussianBlur(image, (0, 0), sigmaX=radius, sigmaY=radius)
        result = cv2.addWeighted(image, 1.0 + amount, blurred, -amount, 0)
        return result.astype(numpy.float32)
