from typing import Optional

import cv2
import numpy
from PySide6TK.Nodes import FieldDefinition
from PySide6TK.Nodes import FieldType
from PySide6TK.Nodes import PortType

from catena.nodes.node_gui import CatenaNode
from catena.nodes.image import IMAGE_NODE_COLOR
from catena.nodes.node_processor import ProcessorNode


class ThresholdProcessor(ProcessorNode):
    """A headless processor that binarizes an image based on a threshold value."""

    def __init__(self, threshold: int = 128, invert: bool = False) -> None:
        super().__init__()
        self.threshold = threshold
        self.invert = invert

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        """
        Binarize an input image based on a threshold value.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Expects key "Input"
                containing a float32 image with values in [0, 1].
        Returns:
            numpy.ndarray | None: A float32 binary mask of shape (H, W, 3)
                with values of 0.0 or 1.0.
        """
        image = inputs.get("Input")
        if image is None:
            return None

        threshold = self.threshold / 255.0
        mode = cv2.THRESH_BINARY_INV if self.invert else cv2.THRESH_BINARY
        gray = image.mean(axis=2)
        _, mask = cv2.threshold(gray, threshold, 1.0, mode)

        return numpy.repeat(mask[:, :, None], 3, axis=2).astype(numpy.float32)


class ThresholdNode(CatenaNode):
    """A node that binarizes an input image based on a threshold value."""

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        self._processor = ThresholdProcessor()
        super().__init__(title="Threshold")

    def _build(self) -> None:
        self.port_in = self.add_port(PortType.INPUT, "Input")
        self.port_out = self.add_port(PortType.OUTPUT, "Output")

        self.add_field(
            FieldDefinition(
                name="threshold",
                label="Threshold",
                field_type=FieldType.INT,
                default=128,
                min_value=0,
                max_value=255,
            )
        )
        self.add_field(
            FieldDefinition(
                name="invert",
                label="Invert",
                field_type=FieldType.BOOL,
                default=False,
            )
        )

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        self._processor.threshold = self.get_field_value("threshold")
        self._processor.invert = self.get_field_value("invert")
        return self._processor.process(inputs)
