from typing import Optional

import numpy
from PySide6TK.Nodes import FieldDefinition
from PySide6TK.Nodes import FieldType
from PySide6TK.Nodes import PortType

from catena.nodes.base import CatenaNode
from catena.nodes.image import IMAGE_NODE_COLOR
from catena.nodes.processor import ProcessorNode


class ContrastProcessor(ProcessorNode):
    """A headless processor that adjusts brightness and contrast of an image."""

    def __init__(self, contrast: float = 1.0, brightness: float = 0.0) -> None:
        super().__init__()
        self.contrast = contrast
        self.brightness = brightness

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        """
        Adjust brightness and contrast of an input image.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Expects key "Input"
                containing a float32 image.
        Returns:
            numpy.ndarray | None: The adjusted float32 image. Values may
                exceed [0, 1] and should be clamped downstream if needed.
        """
        image = inputs.get("Input")
        if image is None:
            return None

        result = image.astype(numpy.float32) * self.contrast + (self.brightness / 255.0)
        return result.astype(numpy.float32)


class ContrastNode(CatenaNode):
    """A node that adjusts brightness and contrast of an input image."""

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        self._processor = ContrastProcessor()
        super().__init__(title="Contrast")

    def _build(self) -> None:
        self.port_in = self.add_port(PortType.INPUT, "Input")
        self.port_out = self.add_port(PortType.OUTPUT, "Output")

        self.add_field(
            FieldDefinition(
                name="contrast",
                label="Contrast",
                field_type=FieldType.FLOAT,
                default=1.0,
                min_value=0.0,
                max_value=4.0,
            )
        )
        self.add_field(
            FieldDefinition(
                name="brightness",
                label="Brightness",
                field_type=FieldType.FLOAT,
                default=0.0,
                min_value=-255.0,
                max_value=255.0,
            )
        )

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        self._processor.contrast = self.get_field_value("contrast")
        self._processor.brightness = self.get_field_value("brightness")
        return self._processor.process(inputs)
