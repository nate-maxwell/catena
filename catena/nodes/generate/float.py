from typing import Optional

import numpy
from PySide6TK.Nodes import FieldDefinition
from PySide6TK.Nodes import FieldType
from PySide6TK.Nodes import PortType

from catena.nodes.node_gui import CatenaNode
from catena.nodes.node_processor import ProcessorNode
from catena.nodes.data import PortDataType
from catena.nodes.math import IMAGE_NODE_COLOR
from catena.preferences import preferences


class FloatProcessor(ProcessorNode):
    """A headless processor that outputs a solid float value as an image."""

    def __init__(self, value: float = 0.0) -> None:
        super().__init__()
        self.value = value

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        """
        Output a solid float value as a grayscale image.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Unused.
        Returns:
            numpy.ndarray | None: A float32 image of shape (H, W, 3) filled
                with the float value, clamped to [0, 1].
        """
        width = preferences.Preferences().general_preferences.texture_resolution
        height = width

        value = numpy.clip(self.value, 0.0, 1.0)
        return numpy.full((height, width, 4), value, dtype=numpy.float32)


class FloatNode(CatenaNode):
    """A node that outputs a solid float value as a grayscale image."""

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        self._processor = FloatProcessor()
        super().__init__(title="Float", width=120, body_height=20)

    def _build(self) -> None:
        self.port_out = self.add_port(PortType.OUTPUT, "Output", PortDataType.FLOAT)

        self.add_field(
            FieldDefinition(
                name="value",
                label="Value",
                field_type=FieldType.FLOAT,
                default=0.0,
                min_value=0.0,
                max_value=1.0,
            )
        )

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        self._processor.value = self.get_field_value("value")
        return self._processor.process(inputs)
