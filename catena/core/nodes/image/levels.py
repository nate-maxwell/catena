from typing import Optional

import numpy
from PySide6TK.Nodes.node import FieldDefinition
from PySide6TK.Nodes.node import FieldType
from PySide6TK.Nodes.node import PortType

from catena.core.nodes.base import CatenaNode
from catena.core.nodes.image import IMAGE_NODE_COLOR


class LevelsNode(CatenaNode):
    """A node that remaps input black/white points and applies gamma."""

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        super().__init__(title="Levels")

    def _build(self) -> None:
        self.port_in = self.add_port(PortType.INPUT, "Input")
        self.port_out = self.add_port(PortType.OUTPUT, "Output")

        self.add_field(
            FieldDefinition(
                name="input_low",
                label="Input Low",
                field_type=FieldType.INT,
                default=0,
                min_value=0,
                max_value=255,
            )
        )
        self.add_field(
            FieldDefinition(
                name="input_high",
                label="Input High",
                field_type=FieldType.INT,
                default=255,
                min_value=0,
                max_value=255,
            )
        )
        self.add_field(
            FieldDefinition(
                name="output_low",
                label="Output Low",
                field_type=FieldType.INT,
                default=0,
                min_value=0,
                max_value=255,
            )
        )
        self.add_field(
            FieldDefinition(
                name="output_high",
                label="Output High",
                field_type=FieldType.INT,
                default=255,
                min_value=0,
                max_value=255,
            )
        )
        self.add_field(
            FieldDefinition(
                name="gamma",
                label="Gamma",
                field_type=FieldType.FLOAT,
                default=1.0,
                min_value=0.01,
                max_value=10.0,
            )
        )

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        image = inputs.get("Input")
        if image is None:
            return None

        in_black = self.get_field_value("input_low") / 255.0
        in_white = self.get_field_value("input_high") / 255.0
        gamma = self.get_field_value("gamma")
        out_black = self.get_field_value("output_low") / 255.0
        out_white = self.get_field_value("output_high") / 255.0

        in_range = max(in_white - in_black, 1e-6)
        out_range = out_white - out_black

        result = image.astype(numpy.float32)
        result = (result - in_black) / in_range
        result = numpy.clip(result, 0.0, 1.0)
        result = numpy.power(result, 1.0 / gamma)
        result = result * out_range + out_black
        result = numpy.clip(result, 0.0, 1.0)

        return result.astype(numpy.float32)
