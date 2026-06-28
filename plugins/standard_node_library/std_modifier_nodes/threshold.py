from typing import Optional

import cv2
import numpy

from catena import api
from std_modifier_nodes import IMAGE_NODE_COLOR


class ThresholdNode(api.CatenaNode):
    """A node that binarizes an input modifier based on a threshold value."""

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:

        super().__init__(title="Threshold")

    def _build(self) -> None:
        self.port_in = self.add_port(api.PortType.INPUT, "Input")
        self.port_out = self.add_port(api.PortType.OUTPUT, "Output")

        self.add_field(
            api.FieldDefinition(
                name="threshold",
                label="Threshold",
                field_type=api.FieldType.INT,
                default=128,
                min_value=0,
                max_value=255,
            )
        )
        self.add_field(
            api.FieldDefinition(
                name="invert",
                label="Invert",
                field_type=api.FieldType.BOOL,
                default=False,
            )
        )

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        """
        Binarize an input modifier based on a threshold value.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Expects key "Input"
                containing a float32 modifier with values in [0, 1].
        Returns:
            numpy.ndarray | None: A float32 binary mask of shape (H, W, 3)
                with values of 0.0 or 1.0.
        """
        threshold = self.get_field_value("threshold")
        invert = self.get_field_value("invert")
        image = inputs.get("Input")
        if image is None:
            return None

        threshold = threshold / 255.0
        mode = cv2.THRESH_BINARY_INV if invert else cv2.THRESH_BINARY
        gray = image.mean(axis=2)
        _, mask = cv2.threshold(gray, threshold, 1.0, mode)

        return numpy.repeat(mask[:, :, None], 4, axis=2).astype(numpy.float32)
