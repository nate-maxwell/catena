from typing import Optional

import numpy
from PySide6TK.Nodes import FieldDefinition
from PySide6TK.Nodes import FieldType
from PySide6TK.Nodes import PortType

from catena.nodes.base import CatenaNode
from catena.nodes.image import IMAGE_NODE_COLOR
from catena.nodes.processor import ProcessorNode


class LevelsProcessor(ProcessorNode):
    """A headless processor that remaps input black/white points and applies gamma."""

    def __init__(
        self,
        input_low: int = 0,
        input_high: int = 255,
        output_low: int = 0,
        output_high: int = 255,
        gamma: float = 1.0,
    ) -> None:
        super().__init__()
        self.input_low = input_low
        self.input_high = input_high
        self.output_low = output_low
        self.output_high = output_high
        self.gamma = gamma

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        """
        Remap input black/white points and apply gamma correction.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Expects key "Input"
                containing a float32 image with values in [0, 1].
        Returns:
            numpy.ndarray | None: The adjusted float32 image clamped to [0, 1].
        """
        image = inputs.get("Input")
        if image is None:
            return None

        in_black = self.input_low / 255.0
        in_white = self.input_high / 255.0
        out_black = self.output_low / 255.0
        out_white = self.output_high / 255.0

        in_range = max(in_white - in_black, 1e-6)
        out_range = out_white - out_black

        result = image.astype(numpy.float32)
        result = (result - in_black) / in_range
        result = numpy.clip(result, 0.0, 1.0)
        result = numpy.power(result, 1.0 / self.gamma)
        result = result * out_range + out_black
        return numpy.clip(result, 0.0, 1.0).astype(numpy.float32)


class LevelsNode(CatenaNode):
    """A node that remaps input black/white points and applies gamma."""

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        self._processor = LevelsProcessor()
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
        self._processor.input_low = self.get_field_value("input_low")
        self._processor.input_high = self.get_field_value("input_high")
        self._processor.output_low = self.get_field_value("output_low")
        self._processor.output_high = self.get_field_value("output_high")
        self._processor.gamma = self.get_field_value("gamma")
        return self._processor.process(inputs)
