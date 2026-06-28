from typing import Optional

import numpy

from catena import api
from std_generate_nodes import IMAGE_NODE_COLOR


class ColorNode(api.CatenaNode):
    """A node that outputs a solid color modifier."""

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        super().__init__(title="Color", width=120, body_height=20)

    def _build(self) -> None:
        self.port_out = self.add_port(api.PortType.OUTPUT, "Color")

        self.add_field(
            api.FieldDefinition(
                name="color",
                label="Color",
                field_type=api.FieldType.COLOR,
                default=(255, 255, 255, 255),
            )
        )

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        """
        Generate a solid color modifier.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Unused; generators
                produce output from parameters only.
        Returns:
            numpy.ndarray | None: A float32 solid color modifier of shape
                (512, 512, 3) with values in [0, 1].
        """
        color = self.get_field_value("color")
        r, g, b, _ = color
        width, height = 512, 512
        result = numpy.zeros((height, width, 4), dtype=numpy.float32)
        result[:, :] = (b / 255.0, g / 255.0, r / 255.0)

        return result
