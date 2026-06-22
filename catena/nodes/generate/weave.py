from typing import Optional

import numpy
from PySide6TK.Nodes import FieldDefinition
from PySide6TK.Nodes import FieldType
from PySide6TK.Nodes import PortType

from catena.nodes.generate.generator import GeneratorNode
from catena.nodes.node_processor import ProcessorNode
from catena.preferences import preferences


class WeaveProcessor(ProcessorNode):
    """A headless processor that generates a woven fabric pattern."""

    def __init__(
        self,
        scale: int = 16,
        width: float = 0.8,
        softness: float = 0.1,
        highlight: float = 0.3,
        gap: float = 0.05,
    ) -> None:
        super().__init__()
        self.scale = scale
        self.width = width
        self.softness = softness
        self.highlight = highlight
        self.gap = gap

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]] | None = None
    ) -> Optional[numpy.ndarray]:
        width = preferences.Preferences().general_preferences.texture_resolution
        height = width

        y_idx, x_idx = numpy.indices((height, width), dtype=numpy.float32)

        x_norm = (x_idx / width) * self.scale
        y_norm = (y_idx / height) * self.scale

        x_cell = numpy.floor(x_norm).astype(int)
        y_cell = numpy.floor(y_norm).astype(int)

        x_local = x_norm - numpy.floor(x_norm)
        y_local = y_norm - numpy.floor(y_norm)

        checker = ((x_cell + y_cell) % 2).astype(numpy.float32)

        soft = max(self.softness, 1e-6)
        half = self.width / 2.0
        gap_half = self.gap / 2.0
        inner = half - gap_half

        def fiber_mask(local: numpy.ndarray) -> numpy.ndarray:
            return numpy.clip((local - (0.5 - inner)) / soft, 0.0, 1.0) * numpy.clip(
                ((0.5 + inner) - local) / soft, 0.0, 1.0
            )

        def fiber_shade(local: numpy.ndarray, mask: numpy.ndarray) -> numpy.ndarray:
            t = (local - (0.5 - inner)) / (inner * 2.0 + 1e-6)
            shading = numpy.sin(numpy.clip(t, 0.0, 1.0) * numpy.pi)
            return mask * (0.6 + shading * self.highlight)

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

        return numpy.repeat(result[:, :, None], 3, axis=2).astype(numpy.float32)


class WeaveNode(GeneratorNode):
    """A node that generates a woven fabric pattern."""

    def __init__(self) -> None:
        self._processor = WeaveProcessor()
        super().__init__(title="Weave")

    def _build(self) -> None:
        self.port_out = self.add_port(PortType.OUTPUT, "Output")

        self.add_field(
            FieldDefinition(
                name="scale",
                label="Scale",
                field_type=FieldType.INT,
                default=16,
                min_value=2,
                max_value=128,
            )
        )
        self.add_field(
            FieldDefinition(
                name="width",
                label="Width",
                field_type=FieldType.FLOAT,
                default=0.8,
                min_value=0.1,
                max_value=1.0,
            )
        )
        self.add_field(
            FieldDefinition(
                name="softness",
                label="Softness",
                field_type=FieldType.FLOAT,
                default=0.1,
                min_value=0.0,
                max_value=0.5,
            )
        )
        self.add_field(
            FieldDefinition(
                name="highlight",
                label="Highlight",
                field_type=FieldType.FLOAT,
                default=0.3,
                min_value=0.0,
                max_value=1.0,
            )
        )
        self.add_field(
            FieldDefinition(
                name="gap",
                label="Gap",
                field_type=FieldType.FLOAT,
                default=0.05,
                min_value=0.0,
                max_value=0.5,
            )
        )

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        self._processor.scale = self.get_field_value("scale")
        self._processor.width = self.get_field_value("width")
        self._processor.softness = self.get_field_value("softness")
        self._processor.highlight = self.get_field_value("highlight")
        self._processor.gap = self.get_field_value("gap")
        return self._processor.process(inputs)
