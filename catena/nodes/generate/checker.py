from typing import Optional

import numpy
from PySide6TK.Nodes import FieldDefinition
from PySide6TK.Nodes import FieldType
from PySide6TK.Nodes import PortType

from catena.nodes.generate.generator import GeneratorNode
from catena.nodes.node_processor import ProcessorNode
from catena.preferences import preferences


class CheckerProcessor(ProcessorNode):
    """A headless processor that generates a checker pattern."""

    def __init__(self, tiles: int = 4, diagonal: bool = False) -> None:
        super().__init__()
        self.tiles = tiles
        self.diagonal = diagonal

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]] | None = None
    ) -> Optional[numpy.ndarray]:
        """
        Generate a black and white checker pattern.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Unused; generators
                produce output from parameters only.
        Returns:
            numpy.ndarray | None: A float32 checker modifier of shape
                (width, height, 3) with values of 0.0 or 1.0.
        """
        width = preferences.Preferences().general_preferences.texture_resolution
        height = width

        y_idx, x_idx = numpy.indices((height, width), dtype=numpy.float32)

        x_norm = x_idx / width * self.tiles
        y_norm = y_idx / height * self.tiles

        if self.diagonal:
            rx = (x_norm + y_norm) / 2.0
            ry = (x_norm - y_norm) / 2.0
        else:
            rx = x_norm
            ry = y_norm

        checker = (numpy.floor(rx) + numpy.floor(ry)).astype(int) % 2
        checker = checker.astype(numpy.float32)

        return numpy.repeat(checker[:, :, None], 4, axis=2).astype(numpy.float32)


class CheckerNode(GeneratorNode):
    """A node that generates a black and white checker pattern."""

    def __init__(self) -> None:
        self._processor = CheckerProcessor()
        super().__init__(title="Checker")

    def _build(self) -> None:
        self.port_out = self.add_port(PortType.OUTPUT, "Output")

        self.add_field(
            FieldDefinition(
                name="tiles",
                label="Tiles",
                field_type=FieldType.INT,
                default=4,
                min_value=2,
                max_value=64,
            )
        )
        self.add_field(
            FieldDefinition(
                name="diagonal",
                label="Diagonal",
                field_type=FieldType.BOOL,
                default=False,
            )
        )

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        self._processor.tiles = self.get_field_value("tiles")
        self._processor.diagonal = self.get_field_value("diagonal")
        return self._processor.process(inputs)
