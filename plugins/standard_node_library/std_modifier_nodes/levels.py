from typing import Optional

import numpy

from catena import api
from std_modifier_nodes import IMAGE_NODE_COLOR


class LevelsNode(api.CatenaNode):
    """A node that remaps input black/white points and applies gamma."""

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:

        super().__init__(title="Levels")

    def _build(self) -> None:
        self.port_in = self.add_port(api.PortType.INPUT, "Input")
        self.port_out = self.add_port(api.PortType.OUTPUT, "Output")

        self.add_field(
            api.FieldDefinition(
                name="input_low",
                label="Input Low",
                field_type=api.FieldType.INT,
                default=0,
                min_value=0,
                max_value=255,
            )
        )
        self.add_field(
            api.FieldDefinition(
                name="input_high",
                label="Input High",
                field_type=api.FieldType.INT,
                default=255,
                min_value=0,
                max_value=255,
            )
        )
        self.add_field(
            api.FieldDefinition(
                name="output_low",
                label="Output Low",
                field_type=api.FieldType.INT,
                default=0,
                min_value=0,
                max_value=255,
            )
        )
        self.add_field(
            api.FieldDefinition(
                name="output_high",
                label="Output High",
                field_type=api.FieldType.INT,
                default=255,
                min_value=0,
                max_value=255,
            )
        )
        self.add_field(
            api.FieldDefinition(
                name="gamma",
                label="Gamma",
                field_type=api.FieldType.FLOAT,
                default=1.0,
                min_value=0.01,
                max_value=10.0,
            )
        )

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        """
        Remap input black/white points and apply gamma correction.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Expects key "Input"
                containing a float32 modifier with values in [0, 1].
        Returns:
            numpy.ndarray | None: The adjusted float32 modifier clamped to [0, 1].
        """
        input_low = self.get_field_value("input_low")
        input_high = self.get_field_value("input_high")
        output_low = self.get_field_value("output_low")
        output_high = self.get_field_value("output_high")
        gamma = self.get_field_value("gamma")

        image = inputs.get("Input")
        if image is None:
            return None

        in_black = input_low / 255.0
        in_white = input_high / 255.0
        out_black = output_low / 255.0
        out_white = output_high / 255.0

        in_range = max(in_white - in_black, 1e-6)
        out_range = out_white - out_black

        result = image.astype(numpy.float32)
        result = (result - in_black) / in_range
        result = numpy.clip(result, 0.0, 1.0)
        result = numpy.power(result, 1.0 / gamma)
        result = result * out_range + out_black
        return numpy.clip(result, 0.0, 1.0).astype(numpy.float32)
