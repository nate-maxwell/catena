from typing import Optional

import numpy

from catena import api
from std_generate_nodes.generator import GeneratorNode


class CheckerNode(GeneratorNode):
    """A node that generates a black and white checker pattern."""

    def __init__(self) -> None:
        super().__init__(title="Checker")

    def _build(self) -> None:
        self.port_out = self.add_port(api.PortType.OUTPUT, "Output")

        self.add_field(
            api.FieldDefinition(
                name="tiles",
                label="Tiles",
                field_type=api.FieldType.INT,
                default=4,
                min_value=2,
                max_value=64,
            )
        )
        self.add_field(
            api.FieldDefinition(
                name="diagonal",
                label="Diagonal",
                field_type=api.FieldType.BOOL,
                default=False,
            )
        )

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
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
        tiles = self.get_field_value("tiles")
        diagonal = self.get_field_value("diagonal")
        width, height = api.get_texture_resolution()

        y_idx, x_idx = numpy.indices((height, width), dtype=numpy.float32)

        x_norm = x_idx / width * tiles
        y_norm = y_idx / height * tiles

        if diagonal:
            rx = (x_norm + y_norm) / 2.0
            ry = (x_norm - y_norm) / 2.0
        else:
            rx = x_norm
            ry = y_norm

        checker = (numpy.floor(rx) + numpy.floor(ry)).astype(int) % 2
        checker = checker.astype(numpy.float32)

        return numpy.repeat(checker[:, :, None], 4, axis=2).astype(numpy.float32)
