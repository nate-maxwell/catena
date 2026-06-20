from typing import Optional

import cv2
import numpy
from PySide6TK.Nodes import FieldDefinition
from PySide6TK.Nodes import FieldType
from PySide6TK.Nodes import PortType

from catena.nodes.base import CatenaNode
from catena.nodes.image import IMAGE_NODE_COLOR
from catena.nodes.processor import ProcessorNode


class BlurProcessor(ProcessorNode):
    """A headless processor that applies a Gaussian blur to an image."""

    def __init__(self, radius: float = 2.0) -> None:
        super().__init__()
        self.radius = radius

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        """
        Apply a Gaussian blur to an input image.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Expects key "Input"
                containing a float32 image.
        Returns:
            numpy.ndarray | None: The blurred float32 image, or None if
                no input is provided.
        """
        image = inputs.get("Input")
        if image is None:
            return None

        if self.radius <= 0:
            return image

        return cv2.GaussianBlur(
            image, (0, 0), sigmaX=self.radius, sigmaY=self.radius
        ).astype(numpy.float32)


class BlurNode(CatenaNode):
    """A node that applies a Gaussian blur to an input image."""

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        self._processor = BlurProcessor()
        super().__init__(title="Blur")

    def _build(self) -> None:
        self.port_in = self.add_port(PortType.INPUT, "Input")
        self.port_out = self.add_port(PortType.OUTPUT, "Output")

        self.add_field(
            FieldDefinition(
                name="radius",
                label="Radius",
                field_type=FieldType.FLOAT,
                default=2.0,
                min_value=0.0,
                max_value=100.0,
            )
        )

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        self._processor.radius = self.get_field_value("radius")
        return self._processor.process(inputs)
