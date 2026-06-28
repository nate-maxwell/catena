from typing import Optional

import cv2
import numpy


from catena import api
from std_modifier_nodes import IMAGE_NODE_COLOR


class QuantizeNode(api.CatenaNode):
    """A node that pixelates an image by quantizing its UV coordinates."""

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:

        super().__init__(title="Retro")

    def _build(self) -> None:
        self.port_in = self.add_port(api.PortType.INPUT, "Input")
        self.port_out = self.add_port(api.PortType.OUTPUT, "Output")

        self.add_field(
            api.FieldDefinition(
                name="factor",
                label="Factor",
                field_type=api.FieldType.INT,
                default=16,
                min_value=1,
                max_value=2048,
            )
        )

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        """
        Pixelate the input image by multiplying UV coordinates by factor,
        flooring to the nearest integer, then dividing back. This snaps each
        pixel to the nearest grid cell of size (1/factor), producing a
        blocky downres appearance without actually changing the output resolution.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Must contain key
                "Input" with a float32 BGR image.
        Returns:
            numpy.ndarray | None: A float32 BGR image of shape (H, W, 3)
                with values in [0, 1], or None if no input is provided.
        """
        factor = self.get_field_value("factor")
        image = inputs.get("Input")
        if image is None:
            return None

        image = numpy.clip(image, 0.0, 1.0).astype(numpy.float32)
        h, w = image.shape[:2]
        factor = max(1, factor)

        y_idx, x_idx = numpy.mgrid[0:h, 0:w].astype(numpy.float32)

        # Normalize to [0, 1] UV space, quantize, then map back to pixel coords
        u = x_idx / w
        v = y_idx / h

        u_q = numpy.floor(u * factor) / factor
        v_q = numpy.floor(v * factor) / factor

        map_x = (u_q * w).astype(numpy.float32)
        map_y = (v_q * h).astype(numpy.float32)

        result = cv2.remap(
            image, map_x, map_y, cv2.INTER_NEAREST, borderMode=cv2.BORDER_REFLECT
        )
        return numpy.clip(result, 0.0, 1.0)
