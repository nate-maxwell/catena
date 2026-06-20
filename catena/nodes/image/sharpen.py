from typing import Optional

import cv2
import numpy
from PySide6TK.Nodes import FieldDefinition
from PySide6TK.Nodes import FieldType
from PySide6TK.Nodes import PortType

from catena.nodes.base import CatenaNode
from catena.nodes.image import IMAGE_NODE_COLOR
from catena.nodes.processor import ProcessorNode


class SharpenProcessor(ProcessorNode):
    """A headless processor that sharpens an image using an unsharp mask."""

    def __init__(self, amount: float = 1.0, radius: float = 2.0) -> None:
        super().__init__()
        self.amount = amount
        self.radius = radius

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        """
        Sharpen an input image using an unsharp mask.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Expects key "Input"
                containing a float32 image.
        Returns:
            numpy.ndarray | None: The sharpened float32 image. Values may
                exceed [0, 1] and should be clamped downstream if needed.
        """
        image = inputs.get("Input")
        if image is None:
            return None

        if self.amount <= 0:
            return image

        blurred = cv2.GaussianBlur(
            image, (0, 0), sigmaX=self.radius, sigmaY=self.radius
        )
        result = cv2.addWeighted(image, 1.0 + self.amount, blurred, -self.amount, 0)
        return result.astype(numpy.float32)


class SharpenNode(CatenaNode):
    """A node that sharpens an input image using an unsharp mask."""

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        self._processor = SharpenProcessor()
        super().__init__(title="Sharpen")

    def _build(self) -> None:
        self.port_in = self.add_port(PortType.INPUT, "Input")
        self.port_out = self.add_port(PortType.OUTPUT, "Output")

        self.add_field(
            FieldDefinition(
                name="amount",
                label="Amount",
                field_type=FieldType.FLOAT,
                default=1.0,
                min_value=0.0,
                max_value=100.0,
            )
        )
        self.add_field(
            FieldDefinition(
                name="radius",
                label="Radius",
                field_type=FieldType.FLOAT,
                default=2.0,
                min_value=0.1,
                max_value=100.0,
            )
        )

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        self._processor.amount = self.get_field_value("amount")
        self._processor.radius = self.get_field_value("radius")
        return self._processor.process(inputs)
