from typing import Optional

import numpy
from PySide6TK.Nodes import FieldDefinition
from PySide6TK.Nodes import FieldType
from PySide6TK.Nodes import PortType

from catena.nodes.generate import IMAGE_NODE_COLOR
from catena.nodes.generate.generator import GeneratorNode
from catena.nodes.node_processor import ProcessorNode
from catena.preferences import preferences


class PinkNoiseProcessor(ProcessorNode):
    """A headless processor that generates 1/f^exponent noise via FFT."""

    def __init__(
        self,
        exponent: float = 1.0,
        seed: int = 0,
    ) -> None:
        super().__init__()
        self.exponent = exponent
        self.seed = seed

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        """
        Generate colored noise by shaping white noise in the frequency domain.
        White noise is transformed via FFT, each frequency bin is scaled by
        f^(-exponent/2) to produce the target power spectral density of
        1/f^exponent, then transformed back via IFFT.

        exponent=0 gives white noise (flat spectrum), exponent=1 gives pink
        noise (1/f), exponent=2 gives brown/red noise (1/f²).

        Args:
            inputs (dict[str, numpy.ndarray | None]): Unused; generators
                produce output from parameters only.
        Returns:
            numpy.ndarray | None: A float32 BGR image of shape (H, W, 3)
                with values in [0, 1].
        """
        width = preferences.Preferences().general_preferences.texture_resolution
        height = width

        rng = numpy.random.default_rng(self.seed)

        white = rng.standard_normal((height, width)).astype(numpy.float32)
        F = numpy.fft.rfft2(white)

        fy = numpy.fft.fftfreq(height).reshape(-1, 1).astype(numpy.float32)
        fx = numpy.fft.rfftfreq(width).reshape(1, -1).astype(numpy.float32)
        freq = numpy.sqrt(fy**2 + fx**2)
        freq[0, 0] = 1.0
        power = freq ** (-self.exponent / 2.0)
        power[0, 0] = 0.0  # zero DC = zero mean

        F *= power
        result = numpy.fft.irfft2(F, s=(height, width)).astype(numpy.float32)
        result -= result.min()
        if result.max() > 0.0:
            result /= result.max()

        return numpy.repeat(result[:, :, None], 4, axis=2)


class PinkNoiseNode(GeneratorNode):
    """A node that generates 1/f^exponent colored noise via FFT shaping."""

    def __init__(self) -> None:
        self._processor = PinkNoiseProcessor()
        super().__init__(title="Pink Noise")

    def _get_node_color(self) -> tuple[int, int, int]:
        return IMAGE_NODE_COLOR

    def _build(self) -> None:
        self.port_out = self.add_port(PortType.OUTPUT, "Output")

        self.add_field(
            FieldDefinition(
                name="exponent",
                label="Exponent",
                field_type=FieldType.FLOAT,
                default=1.0,
                min_value=0.0,
                max_value=4.0,
            )
        )
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
        self._processor.exponent = self.get_field_value("exponent")

        seed = self.get_field_value("seed")
        self._processor.seed = int(seed * 255) if isinstance(seed, float) else int(seed)

        return self._processor.process(inputs)
