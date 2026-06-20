from typing import Optional

import numpy
from PySide6TK.Nodes import FieldDefinition
from PySide6TK.Nodes import FieldType
from PySide6TK.Nodes import PortType

from catena.application.nodes.generate.generator import GeneratorNode


class WhiteNoiseNode(GeneratorNode):
    """A node that generates uniform random white noise."""

    def __init__(self) -> None:
        super().__init__(title="White Noise")

    def _build(self) -> None:
        self.port_out = self.add_port(PortType.OUTPUT, "Output")

        self.add_field(
            FieldDefinition(
                name="seed",
                label="Seed",
                field_type=FieldType.INT,
                default=0,
                min_value=0,
                max_value=99999,
            )
        )

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        seed = self.get_field_value("seed")

        width, height = 512, 512
        rng = numpy.random.default_rng(seed)

        gray = rng.random((height, width), dtype=numpy.float32)
        result = numpy.repeat(gray[:, :, None], 3, axis=2).astype(numpy.float32)
        return result
