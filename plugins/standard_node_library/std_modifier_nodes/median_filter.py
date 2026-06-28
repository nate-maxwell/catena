from typing import Optional

import cv2
import numpy

from catena import api
from std_modifier_nodes import IMAGE_NODE_COLOR


class MedianFilterNode(api.CatenaNode):
    """A node that applies a median filter for edge-preserving noise reduction."""

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:

        super().__init__(title="Median Filter")

    def _build(self) -> None:
        self.port_in = self.add_port(api.PortType.INPUT, "Input")
        self.port_out = self.add_port(api.PortType.OUTPUT, "Output")

        self.add_field(
            api.FieldDefinition(
                name="radius",
                label="Radius",
                field_type=api.FieldType.INT,
                default=4,
                min_value=1,
                max_value=50,
            )
        )

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        """
        Apply a median filter. Each pixel is replaced by the median of all
        pixels within a square kernel of size (radius*2+1). Preserves hard
        edges while removing noise, unlike Gaussian or box blur.

        cv2.medianBlur requires uint8, so the image is converted, filtered,
        and converted back.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Must contain key
                "Input" with a float32 BGR image.
        Returns:
            numpy.ndarray | None: A float32 BGR image of shape (H, W, 3)
                with values in [0, 1], or None if no input is provided.
        """
        radius = self.get_field_value("radius")

        image = inputs.get("Input")
        if image is None:
            return None

        ksize = max(1, int(radius)) * 2 + 1
        u8 = (numpy.clip(image, 0.0, 1.0) * 255).astype(numpy.uint8)
        result = cv2.medianBlur(u8, ksize)
        return (result / 255.0).astype(numpy.float32)
