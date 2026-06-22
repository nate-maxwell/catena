from typing import Optional

import numpy
from PySide6TK.Nodes import FieldDefinition
from PySide6TK.Nodes import FieldType
from PySide6TK.Nodes import PortType

from catena.nodes.node_gui import CatenaNode
from catena.nodes.generate import IMAGE_NODE_COLOR
from catena.nodes.node_processor import ProcessorNode


class ColorProcessor(ProcessorNode):
    """A headless processor that outputs a solid color image."""

    def __init__(self, color: tuple[int, int, int, int] = (255, 255, 255, 255)) -> None:
        super().__init__()
        self.color = color

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        """
        Generate a solid color image.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Unused; generators
                produce output from parameters only.
        Returns:
            numpy.ndarray | None: A float32 solid color image of shape
                (512, 512, 3) with values in [0, 1].
        """
        r, g, b, _ = self.color

        width, height = 512, 512
        result = numpy.zeros((height, width, 3), dtype=numpy.float32)
        result[:, :] = (b / 255.0, g / 255.0, r / 255.0)

        return result


class ColorNode(CatenaNode):
    """A node that outputs a solid color image."""

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        self._processor = ColorProcessor()
        super().__init__(title="Color", width=120, body_height=20)

    def _build(self) -> None:
        self.port_out = self.add_port(PortType.OUTPUT, "Color")

        self.add_field(
            FieldDefinition(
                name="color",
                label="Color",
                field_type=FieldType.COLOR,
                default=(255, 255, 255, 255),
            )
        )

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        self._processor.color = self.get_field_value("color")
        return self._processor.process(inputs)
