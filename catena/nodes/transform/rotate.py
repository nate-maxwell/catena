from typing import Optional

import cv2
import numpy
from PySide6TK.Nodes import FieldDefinition
from PySide6TK.Nodes import FieldType
from PySide6TK.Nodes import PortType

from catena.nodes.node_gui import CatenaNode
from catena.nodes.node_processor import ProcessorNode
from catena.nodes.transform import IMAGE_NODE_COLOR


class RotateProcessor(ProcessorNode):
    """A headless processor that rotates an image by an arbitrary angle."""

    def __init__(self, angle: float = 0.0, scale: float = 1.0) -> None:
        super().__init__()
        self.angle = angle
        self.scale = scale

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        """
        Rotate an input image by an arbitrary angle.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Expects key "Input"
                containing a float32 image.
        Returns:
            numpy.ndarray | None: The rotated float32 image.
        """
        image = inputs.get("Input")
        if image is None:
            return None

        height, width = image.shape[:2]
        center = (width / 2.0, height / 2.0)

        matrix = cv2.getRotationMatrix2D(center, self.angle, self.scale)
        return cv2.warpAffine(image, matrix, (width, height)).astype(numpy.float32)


class RotateNode(CatenaNode):
    """A node that rotates an input image by an arbitrary angle."""

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        self._processor = RotateProcessor()
        super().__init__(title="Rotate")

    def _build(self) -> None:
        self.port_in = self.add_port(PortType.INPUT, "Input")
        self.port_out = self.add_port(PortType.OUTPUT, "Output")

        self.add_field(
            FieldDefinition(
                name="angle",
                label="Angle",
                field_type=FieldType.FLOAT,
                default=0.0,
                min_value=-360.0,
                max_value=360.0,
            )
        )
        self.add_field(
            FieldDefinition(
                name="scale",
                label="Scale",
                field_type=FieldType.FLOAT,
                default=1.0,
                min_value=0.01,
                max_value=10.0,
            )
        )

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        self._processor.angle = self.get_field_value("angle")
        self._processor.scale = self.get_field_value("scale")
        return self._processor.process(inputs)
