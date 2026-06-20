from typing import Optional

import cv2
import numpy
from PySide6TK.Nodes import FieldDefinition
from PySide6TK.Nodes import FieldType
from PySide6TK.Nodes import PortType

from catena.nodes.node_gui import CatenaNode
from catena.nodes.node_processor import ProcessorNode
from catena.nodes.transform import IMAGE_NODE_COLOR

_FLIP_CODES = {"Horizontal": 1, "Vertical": 0, "Both": -1}


class FlipProcessor(ProcessorNode):
    """A headless processor that flips an image horizontally, vertically, or both."""

    def __init__(self, direction: str = "Horizontal") -> None:
        super().__init__()
        self.direction = direction

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        """
        Flip an input image horizontally, vertically, or both.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Expects key "Input"
                containing a float32 image.
        Returns:
            numpy.ndarray | None: The flipped float32 image.
        """
        image = inputs.get("Input")
        if image is None:
            return None

        return cv2.flip(image, _FLIP_CODES[self.direction]).astype(numpy.float32)


class FlipNode(CatenaNode):
    """A node that flips an input image horizontally, vertically, or both."""

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        self._processor = FlipProcessor()
        super().__init__(title="Flip")

    def _build(self) -> None:
        self.port_in = self.add_port(PortType.INPUT, "Input")
        self.port_out = self.add_port(PortType.OUTPUT, "Output")

        self.add_field(
            FieldDefinition(
                name="direction",
                label="Direction",
                field_type=FieldType.CHOICE,
                default="Horizontal",
                options=["Horizontal", "Vertical", "Both"],
            )
        )

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        self._processor.direction = self.get_field_value("direction")
        return self._processor.process(inputs)
