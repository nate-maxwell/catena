from typing import Optional

import numpy

from catena import api
from std_generate_nodes.generator import GeneratorNode


class GaussianNoiseNode(GeneratorNode):
    """A node that generates grayscale Gaussian noise."""

    def __init__(self) -> None:
        super().__init__(title="Gaussian Noise")

    def _build(self) -> None:
        self.port_out = self.add_port(api.PortType.OUTPUT, "Output")

        self.add_field(
            api.FieldDefinition(
                name="mean",
                label="Mean",
                field_type=api.FieldType.FLOAT,
                default=0.5,
                min_value=0.0,
                max_value=1.0,
            )
        )
        self.add_field(
            api.FieldDefinition(
                name="sigma",
                label="Sigma",
                field_type=api.FieldType.FLOAT,
                default=0.15,
                min_value=0.0,
                max_value=1.0,
            )
        )
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
        Generate Gaussian-distributed grayscale noise.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Unused; generators
                produce output from parameters only.
        Returns:
            numpy.ndarray | None: A float32 noise modifier of shape
                (height, width, 4) with values in [0, 1].
        """
        mean = float(self.get_field_value("mean"))
        sigma = float(self.get_field_value("sigma"))
        seed = self.get_field_value("seed")
        seed = int(seed * 255) if isinstance(seed, float) else int(seed)

        width, height = api.get_texture_resolution()
        rng = numpy.random.default_rng(seed)
        noise = rng.normal(loc=mean, scale=sigma, size=(height, width))
        gray = numpy.clip(noise, 0.0, 1.0).astype(numpy.float32)

        return numpy.repeat(gray[:, :, None], 4, axis=2)
