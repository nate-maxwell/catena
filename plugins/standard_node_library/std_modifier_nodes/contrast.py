from typing import Optional

import numpy

from catena import api
from std_modifier_nodes import IMAGE_NODE_COLOR


class ContrastNode(api.CatenaNode):
    """A node that adjusts brightness and contrast of an input modifier."""

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:

        super().__init__(title="Contrast")

    def _build(self) -> None:
        self.port_in = self.add_port(api.PortType.INPUT, "Input")
        self.port_out = self.add_port(api.PortType.OUTPUT, "Output")

        self.add_field(
            api.FieldDefinition(
                name="contrast",
                label="Contrast",
                field_type=api.FieldType.FLOAT,
                default=1.0,
                min_value=0.0,
                max_value=4.0,
            )
        )
        self.add_field(
            api.FieldDefinition(
                name="brightness",
                label="Brightness",
                field_type=api.FieldType.FLOAT,
                default=0.0,
                min_value=-255.0,
                max_value=255.0,
            )
        )

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        """
        Adjust brightness and contrast of an input modifier.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Expects key "Input"
                containing a float32 modifier.
        Returns:
            numpy.ndarray | None: The adjusted float32 modifier. Values may
                exceed [0, 1] and should be clamped downstream if needed.
        """
        contrast = self.get_field_value("contrast")
        brightness = self.get_field_value("brightness")

        image = inputs.get("Input")
        if image is None:
            return None

        result = image.astype(numpy.float32) * contrast + (brightness / 255.0)
        return result.astype(numpy.float32)
