from typing import Optional

import numpy

from catena import api
from std_generate_nodes.generator import GeneratorNode


class WhiteNoiseNode(GeneratorNode):
    """A node that generates uniform random white noise."""

    def __init__(self) -> None:
        super().__init__(title="White Noise")

    def _build(self) -> None:
        self.port_out = self.add_port(api.PortType.OUTPUT, "Output")

        self.add_field(
            api.FieldDefinition(
                name="seed",
                label="Seed",
                field_type=api.FieldType.INT,
                default=0,
                min_value=0,
                max_value=99999,
            )
        )

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
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
        seed = self.get_field_value("seed")
        seed = int(seed * 255) if isinstance(seed, float) else int(seed)
        width, height = api.get_texture_resolution()
        rng = numpy.random.default_rng(seed)
        gray = rng.random((height, width), dtype=numpy.float32)

        return numpy.repeat(gray[:, :, None], 4, axis=2).astype(numpy.float32)
