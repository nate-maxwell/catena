from typing import Optional

import cv2
import numpy
from PySide6TK.Nodes import FieldDefinition
from PySide6TK.Nodes import FieldType
from PySide6TK.Nodes import PortType

from catena.nodes.modifier import IMAGE_NODE_COLOR
from catena.nodes.node_gui import CatenaNode
from catena.nodes.node_processor import ProcessorNode


class MedianFilterProcessor(ProcessorNode):
    """A headless processor that applies a median filter to reduce noise."""

    def __init__(
        self,
        radius: int = 4,
    ) -> None:
        super().__init__()
        self.radius = radius

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        """
        Apply a median filter. Each pixel is replaced by the median of all
        pixels within a square kernel of size (radius*2+1). Preserves hard
        edges while removing noise, unlike Gaussian or box blur.

        cv2.medianBlur requires uint8, so the image is converted, filtered,
        and converted back.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Must contain key
                "Input" with a float32 BGR image.
        Returns:
            numpy.ndarray | None: A float32 BGR image of shape (H, W, 3)
                with values in [0, 1], or None if no input is provided.
        """
        image = inputs.get("Input")
        if image is None:
            return None

        ksize = max(1, int(self.radius)) * 2 + 1
        u8 = (numpy.clip(image, 0.0, 1.0) * 255).astype(numpy.uint8)
        result = cv2.medianBlur(u8, ksize)
        return (result / 255.0).astype(numpy.float32)


class MedianFilterNode(CatenaNode):
    """A node that applies a median filter for edge-preserving noise reduction."""

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        self._processor = MedianFilterProcessor()
        super().__init__(title="Median Filter")

    def _build(self) -> None:
        self.port_in = self.add_port(PortType.INPUT, "Input")
        self.port_out = self.add_port(PortType.OUTPUT, "Output")

        self.add_field(
            FieldDefinition(
                name="radius",
                label="Radius",
                field_type=FieldType.INT,
                default=4,
                min_value=1,
                max_value=50,
            )
        )

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        self._processor.radius = self.get_field_value("radius")
        return self._processor.process(inputs)
