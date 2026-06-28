from typing import Optional

import numpy

from catena import api
from std_transform_nodes import IMAGE_NODE_COLOR


class OffsetNode(api.CatenaNode):
    """A node that offsets an input modifier, optionally wrapping content around."""

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:

        super().__init__(title="Offset")

    def _build(self) -> None:
        self.port_in = self.add_port(api.PortType.INPUT, "Input")
        self.port_out = self.add_port(api.PortType.OUTPUT, "Output")

        self.add_field(
            api.FieldDefinition(
                name="offset_x",
                label="X",
                field_type=api.FieldType.INT,
                default=0,
            )
        )
        self.add_field(
            api.FieldDefinition(
                name="offset_y",
                label="Y",
                field_type=api.FieldType.INT,
                default=0,
            )
        )
        self.add_field(
            api.FieldDefinition(
                name="wrap",
                label="Wrap",
                field_type=api.FieldType.BOOL,
                default=True,
            )
        )

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        """
        Offset an input modifier by a given amount, optionally wrapping content.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Expects key "Input"
                containing a float32 modifier.
        Returns:
            numpy.ndarray | None: The offset float32 modifier. Non-wrapped regions
                outside the original bounds are filled with black.
        """
        offset_x = self.get_field_value("offset_x")
        offset_y = self.get_field_value("offset_y")
        wrap = self.get_field_value("wrap")

        image = inputs.get("Input")
        if image is None:
            return None

        if wrap:
            return numpy.roll(image, shift=(offset_y, offset_x), axis=(0, 1)).astype(
                numpy.float32
            )

        result = numpy.zeros_like(image)
        height, width = image.shape[:2]

        src_x0 = max(0, -offset_x)
        src_x1 = min(width, width - offset_x)
        src_y0 = max(0, -offset_y)
        src_y1 = min(height, height - offset_y)

        dst_x0 = max(0, offset_x)
        dst_x1 = dst_x0 + (src_x1 - src_x0)
        dst_y0 = max(0, offset_y)
        dst_y1 = dst_y0 + (src_y1 - src_y0)

        if src_x1 > src_x0 and src_y1 > src_y0:
            result[dst_y0:dst_y1, dst_x0:dst_x1] = image[src_y0:src_y1, src_x0:src_x1]

        return result.astype(numpy.float32)
