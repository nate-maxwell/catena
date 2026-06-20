from typing import Optional

import numpy
from PySide6TK.Nodes import FieldDefinition
from PySide6TK.Nodes import FieldType
from PySide6TK.Nodes import PortType

from catena.nodes.generate.generator import GeneratorNode
from catena.nodes.processor import ProcessorNode


class BlueNoiseProcessor(ProcessorNode):
    """A headless processor that generates blue noise via frequency-domain filtering."""

    def __init__(self, seed: int = 0, contrast: float = 1.0) -> None:
        super().__init__()
        self.seed = seed
        self.contrast = contrast

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        """
        Generate blue noise via FFT-based high-pass filtering of white noise.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Unused; generators
                produce output from parameters only.
        Returns:
            numpy.ndarray | None: A float32 blue noise image of shape
                (512, 512, 3) with values in [0, 1].
        """
        width, height = 512, 512
        rng = numpy.random.default_rng(self.seed)

        white = rng.random((height, width)).astype(numpy.float32)

        spectrum = numpy.fft.fft2(white)
        spectrum = numpy.fft.fftshift(spectrum)

        cy, cx = height / 2.0, width / 2.0
        y_idx, x_idx = numpy.indices((height, width))
        dist = numpy.sqrt((y_idx - cy) ** 2 + (x_idx - cx) ** 2)
        max_dist = numpy.sqrt(cx**2 + cy**2)
        radial = dist / max_dist

        high_pass = radial**self.contrast

        filtered = spectrum * high_pass
        filtered = numpy.fft.ifftshift(filtered)
        result = numpy.fft.ifft2(filtered).real

        result -= result.min()
        if result.max() > 0:
            result /= result.max()

        gray = result.astype(numpy.float32)
        return numpy.repeat(gray[:, :, None], 3, axis=2).astype(numpy.float32)


class BlueNoiseNode(GeneratorNode):
    """A node that generates blue noise via frequency-domain filtering."""

    def __init__(self) -> None:
        self._processor = BlueNoiseProcessor()
        super().__init__(title="Blue Noise")

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
        self.add_field(
            FieldDefinition(
                name="contrast",
                label="Contrast",
                field_type=FieldType.FLOAT,
                default=1.0,
                min_value=0.1,
                max_value=4.0,
            )
        )

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        self._processor.seed = self.get_field_value("seed")
        self._processor.contrast = self.get_field_value("contrast")
        return self._processor.process(inputs)
