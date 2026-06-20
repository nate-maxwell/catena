from typing import Optional

import cv2
import numpy
from PySide6TK.Nodes import FieldDefinition
from PySide6TK.Nodes import FieldType
from PySide6TK.Nodes import PortType

from catena.nodes.base import CatenaNode
from catena.nodes.image import IMAGE_NODE_COLOR
from catena.nodes.processor import ProcessorNode


class HSVProcessor(ProcessorNode):
    """A headless processor that shifts hue, saturation, and value of an image."""

    def __init__(
        self,
        hue_shift: int = 0,
        saturation: float = 1.0,
        value: float = 1.0,
    ) -> None:
        super().__init__()
        self.hue_shift = hue_shift
        self.saturation = saturation
        self.value = value

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        """
        Shift hue, saturation, and value of an input image.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Expects key "Input"
                containing a float32 BGR image with values in [0, 1].
        Returns:
            numpy.ndarray | None: The adjusted float32 BGR image with
                values in [0, 1].
        """
        image = inputs.get("Input")
        if image is None:
            return None

        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        hsv[..., 0] = (hsv[..., 0] + self.hue_shift * 2.0) % 360.0
        hsv[..., 1] = numpy.clip(hsv[..., 1] * self.saturation, 0.0, 1.0)
        hsv[..., 2] = numpy.clip(hsv[..., 2] * self.value, 0.0, 1.0)

        return cv2.cvtColor(hsv.astype(numpy.float32), cv2.COLOR_HSV2BGR).astype(
            numpy.float32
        )


class HSVNode(CatenaNode):
    """A node that shifts hue, saturation, and value of an input image."""

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        self._processor = HSVProcessor()
        super().__init__(title="HSV")

    def _build(self) -> None:
        self.port_in = self.add_port(PortType.INPUT, "Input")
        self.port_out = self.add_port(PortType.OUTPUT, "Output")

        self.add_field(
            FieldDefinition(
                name="hue_shift",
                label="Hue Shift",
                field_type=FieldType.INT,
                default=0,
                min_value=-180,
                max_value=180,
            )
        )
        self.add_field(
            FieldDefinition(
                name="saturation",
                label="Saturation",
                field_type=FieldType.FLOAT,
                default=1.0,
                min_value=0.0,
                max_value=3.0,
            )
        )
        self.add_field(
            FieldDefinition(
                name="value",
                label="Value",
                field_type=FieldType.FLOAT,
                default=1.0,
                min_value=0.0,
                max_value=3.0,
            )
        )

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        self._processor.hue_shift = self.get_field_value("hue_shift")
        self._processor.saturation = self.get_field_value("saturation")
        self._processor.value = self.get_field_value("value")
        return self._processor.process(inputs)
