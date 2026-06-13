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
        super().__init__(title="Levels", width=180, body_height=40)

    def _build(self) -> None:
        self.port_in = self.add_port(PortType.INPUT, "Image")
        self.port_out = self.add_port(PortType.OUTPUT, "Image")

        self.add_field(
            FieldDefinition(
                name="input_black",
                label="Input Black",
                field_type=FieldType.INT,
                default=0,
                min_value=0,
                max_value=255,
            )
        )
        self.add_field(
            FieldDefinition(
                name="input_white",
                label="Input White",
                field_type=FieldType.INT,
                default=255,
                min_value=0,
                max_value=255,
            )
        )
        self.add_field(
            FieldDefinition(
                name="output_black",
                label="Output Black",
                field_type=FieldType.INT,
                default=0,
                min_value=0,
                max_value=255,
            )
        )
        self.add_field(
            FieldDefinition(
                name="output_white",
                label="Output White",
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
        image = inputs.get("Image")
        if image is None:
            return None

        in_black = self.get_field_value("input_black")
        in_white = self.get_field_value("input_white")
        gamma = self.get_field_value("gamma")
        out_black = self.get_field_value("output_black")
        out_white = self.get_field_value("output_white")

        in_range = max(in_white - in_black, 1)
        out_range = out_white - out_black

        result = image.astype(numpy.float32)
        result = (result - in_black) / in_range
        result = numpy.clip(result, 0.0, 1.0)
        result = numpy.power(result, 1.0 / gamma)
        result = result * out_range + out_black
        result = numpy.clip(result, 0, 255).astype(numpy.uint8)

        return result
