from typing import Optional

import numpy

from catena import api
from std_generate_nodes.generator import GeneratorNode


class WeaveNode(GeneratorNode):
    """A node that generates a woven fabric pattern."""

    def __init__(self) -> None:
        super().__init__(title="Weave")

    def _build(self) -> None:
        self.port_out = self.add_port(api.PortType.OUTPUT, "Output")

        self.add_field(
            api.FieldDefinition(
                name="scale",
                label="Scale",
                field_type=api.FieldType.INT,
                default=16,
                min_value=2,
                max_value=128,
            )
        )
        self.add_field(
            api.FieldDefinition(
                name="width",
                label="Width",
                field_type=api.FieldType.FLOAT,
                default=0.8,
                min_value=0.1,
                max_value=1.0,
            )
        )
        self.add_field(
            api.FieldDefinition(
                name="softness",
                label="Softness",
                field_type=api.FieldType.FLOAT,
                default=0.1,
                min_value=0.0,
                max_value=0.5,
            )
        )
        self.add_field(
            api.FieldDefinition(
                name="highlight",
                label="Highlight",
                field_type=api.FieldType.FLOAT,
                default=0.3,
                min_value=0.0,
                max_value=1.0,
            )
        )
        self.add_field(
            api.FieldDefinition(
                name="gap",
                label="Gap",
                field_type=api.FieldType.FLOAT,
                default=0.05,
                min_value=0.0,
                max_value=0.5,
            )
        )

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        scale = self.get_field_value("scale")
        width = self.get_field_value("width")
        softness = self.get_field_value("softness")
        highlight = self.get_field_value("highlight")
        gap = self.get_field_value("gap")
        rwidth, height = api.get_texture_resolution()

        y_idx, x_idx = numpy.indices((height, width), dtype=numpy.float32)

        x_norm = (x_idx / width) * scale
        y_norm = (y_idx / height) * scale
        x_cell = numpy.floor(x_norm).astype(int)
        y_cell = numpy.floor(y_norm).astype(int)
        x_local = x_norm - numpy.floor(x_norm)
        y_local = y_norm - numpy.floor(y_norm)

        checker = ((x_cell + y_cell) % 2).astype(numpy.float32)

        soft = max(softness, 1e-6)
        half = width / 2.0
        gap_half = gap / 2.0
        inner = half - gap_half

        def fiber_mask(local: numpy.ndarray) -> numpy.ndarray:
            return numpy.clip((local - (0.5 - inner)) / soft, 0.0, 1.0) * numpy.clip(
                ((0.5 + inner) - local) / soft, 0.0, 1.0
            )

        def fiber_shade(local: numpy.ndarray, mask: numpy.ndarray) -> numpy.ndarray:
            t = (local - (0.5 - inner)) / (inner * 2.0 + 1e-6)
            shading = numpy.sin(numpy.clip(t, 0.0, 1.0) * numpy.pi)
            return mask * (0.6 + shading * highlight)

        h_mask = fiber_mask(y_local)
        v_mask = fiber_mask(x_local)

        h_shade = fiber_shade(y_local, h_mask)
        v_shade = fiber_shade(x_local, v_mask)

        in_h = h_mask > 0.01
        in_v = v_mask > 0.01

        result = numpy.zeros((height, width), dtype=numpy.float32)

        result = numpy.where(in_h & ~in_v, h_shade, result)
        result = numpy.where(in_v & ~in_h, v_shade, result)
        result = numpy.where(
            in_h & in_v,
            numpy.where(checker > 0.5, h_shade, v_shade),
            result,
        )

        return numpy.repeat(result[:, :, None], 4, axis=2).astype(numpy.float32)
