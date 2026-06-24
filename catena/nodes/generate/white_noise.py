from typing import Optional

import numpy
from PySide6TK.Nodes import FieldDefinition
from PySide6TK.Nodes import FieldType
from PySide6TK.Nodes import PortType

from catena.nodes.generate.generator import GeneratorNode
from catena.nodes.node_processor import ProcessorNode
from catena.preferences import preferences


class WhiteNoiseProcessor(ProcessorNode):
    """A headless processor that generates uniform random white noise."""

    def __init__(self, seed: int = 0) -> None:
        super().__init__()
        self.seed = seed

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]] | None = None
    ) -> Optional[numpy.ndarray]:
        """
        Generate uniform random white noise.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Unused; generators
                produce output from parameters only.
        Returns:
            numpy.ndarray | None: A float32 white noise modifier of shape
                (width, height, 3) with values in [0, 1).
        """
        width = preferences.Preferences().general_preferences.texture_resolution
        height = width
        rng = numpy.random.default_rng(self.seed)

        gray = rng.random((height, width), dtype=numpy.float32)
        return numpy.repeat(gray[:, :, None], 3, axis=2).astype(numpy.float32)


class WhiteNoiseNode(GeneratorNode):
    """A node that generates uniform random white noise."""

    def __init__(self) -> None:
        self._processor = WhiteNoiseProcessor()
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
        self._processor.seed = int(seed * 255) if isinstance(seed, float) else int(seed)

        return self._processor.process(inputs)
