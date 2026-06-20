from typing import Optional

import numpy
from PySide6TK.Nodes import FieldDefinition
from PySide6TK.Nodes import FieldType
from PySide6TK.Nodes import PortType

from catena.nodes.generate.generator import GeneratorNode


class BlueNoiseNode(GeneratorNode):
    """A node that generates blue noise via frequency-domain filtering."""

    def __init__(self) -> None:
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
        seed = self.get_field_value("seed")
        contrast = self.get_field_value("contrast")

        width, height = 512, 512
        rng = numpy.random.default_rng(seed)

        white = rng.random((height, width)).astype(numpy.float32)

        spectrum = numpy.fft.fft2(white)
        spectrum = numpy.fft.fftshift(spectrum)

        cy, cx = height / 2.0, width / 2.0
        y_idx, x_idx = numpy.indices((height, width))
        dist = numpy.sqrt((y_idx - cy) ** 2 + (x_idx - cx) ** 2)
        max_dist = numpy.sqrt(cx**2 + cy**2)
        radial = dist / max_dist

        high_pass = radial**contrast

        filtered = spectrum * high_pass
        filtered = numpy.fft.ifftshift(filtered)
        result = numpy.fft.ifft2(filtered).real

        result -= result.min()
        if result.max() > 0:
            result /= result.max()

        gray = result.astype(numpy.float32)
        output = numpy.repeat(gray[:, :, None], 3, axis=2).astype(numpy.float32)
        return output
