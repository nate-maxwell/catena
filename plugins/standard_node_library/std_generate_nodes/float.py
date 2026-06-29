from typing import Optional

import numpy

from catena import api
from std_math_nodes import IMAGE_NODE_COLOR


class FloatNode(api.CatenaNode):
    """A node that outputs a solid float value as a grayscale image."""

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        super().__init__(title="Float", width=120, body_height=20)

    def _build(self) -> None:
        self.port_out = self.add_port(
            api.PortType.OUTPUT, "Output", api.PortDataType.FLOAT
        )

        self.add_field(
            api.FieldDefinition(
                name="value",
                label="Value",
                field_type=api.FieldType.FLOAT,
                default=0.0,
                min_value=0.0,
                max_value=999999.0,
            )
        )

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        """
        Output a solid float value as a grayscale image.

        Args:
           inputs (dict[str, numpy.ndarray | None]): Unused.
        Returns:
           numpy.ndarray | None: A float32 image of shape (H, W, 3) filled
               with the float value, clamped to [0, 1].
        """

        value = self.get_field_value("value")
        width, height = api.get_texture_resolution()
        value = numpy.clip(value, 0.0, 1.0)
        return numpy.full((height, width, 4), value, dtype=numpy.float32)
