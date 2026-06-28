from typing import Optional

import cv2
import numpy


from catena import api
from std_modifier_nodes import IMAGE_NODE_COLOR


class BlurNode(api.CatenaNode):
    """A node that applies a Gaussian blur to an input modifier."""

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:

        super().__init__(title="Blur")

    def _build(self) -> None:
        self.port_in = self.add_port(api.PortType.INPUT, "Input")
        self.port_out = self.add_port(api.PortType.OUTPUT, "Output")

        self.add_field(
            api.FieldDefinition(
                name="radius",
                label="Radius",
                field_type=api.FieldType.FLOAT,
                default=2.0,
                min_value=0.0,
                max_value=100.0,
            )
        )

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        """
        Apply a Gaussian blur to an input modifier.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Expects key "Input"
                containing a float32 modifier.
        Returns:
            numpy.ndarray | None: The blurred float32 modifier, or None if
                no input is provided.
        """
        radius = self.get_field_value("radius")
        image = inputs.get("Input")
        if image is None:
            return None

        if radius <= 0:
            return image

        return cv2.GaussianBlur(image, (0, 0), sigmaX=radius, sigmaY=radius).astype(
            numpy.float32
        )
