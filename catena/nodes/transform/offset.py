from typing import Optional

import numpy
from PySide6TK.Nodes import FieldDefinition
from PySide6TK.Nodes import FieldType
from PySide6TK.Nodes import PortType

from catena.nodes.node_gui import CatenaNode
from catena.nodes.node_processor import ProcessorNode
from catena.nodes.transform import IMAGE_NODE_COLOR


class OffsetProcessor(ProcessorNode):
    """A headless processor that offsets an image, optionally wrapping content around."""

    def __init__(self, offset_x: int = 0, offset_y: int = 0, wrap: bool = True) -> None:
        super().__init__()
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.wrap = wrap

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        """
        Offset an input image by a given amount, optionally wrapping content.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Expects key "Input"
                containing a float32 image.
        Returns:
            numpy.ndarray | None: The offset float32 image. Non-wrapped regions
                outside the original bounds are filled with black.
        """
        image = inputs.get("Input")
        if image is None:
            return None

        if self.wrap:
            return numpy.roll(
                image, shift=(self.offset_y, self.offset_x), axis=(0, 1)
            ).astype(numpy.float32)

        result = numpy.zeros_like(image)
        height, width = image.shape[:2]

        src_x0 = max(0, -self.offset_x)
        src_x1 = min(width, width - self.offset_x)
        src_y0 = max(0, -self.offset_y)
        src_y1 = min(height, height - self.offset_y)

        dst_x0 = max(0, self.offset_x)
        dst_x1 = dst_x0 + (src_x1 - src_x0)
        dst_y0 = max(0, self.offset_y)
        dst_y1 = dst_y0 + (src_y1 - src_y0)

        if src_x1 > src_x0 and src_y1 > src_y0:
            result[dst_y0:dst_y1, dst_x0:dst_x1] = image[src_y0:src_y1, src_x0:src_x1]

        return result.astype(numpy.float32)


class OffsetNode(CatenaNode):
    """A node that offsets an input image, optionally wrapping content around."""

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        self._processor = OffsetProcessor()
        super().__init__(title="Offset")

    def _build(self) -> None:
        self.port_in = self.add_port(PortType.INPUT, "Input")
        self.port_out = self.add_port(PortType.OUTPUT, "Output")

        self.add_field(
            FieldDefinition(
                name="offset_x",
                label="X",
                field_type=FieldType.INT,
                default=0,
            )
        )
        self.add_field(
            FieldDefinition(
                name="offset_y",
                label="Y",
                field_type=FieldType.INT,
                default=0,
            )
        )
        self.add_field(
            FieldDefinition(
                name="wrap",
                label="Wrap",
                field_type=FieldType.BOOL,
                default=True,
            )
        )

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        self._processor.offset_x = self.get_field_value("offset_x")
        self._processor.offset_y = self.get_field_value("offset_y")
        self._processor.wrap = self.get_field_value("wrap")
        return self._processor.process(inputs)
