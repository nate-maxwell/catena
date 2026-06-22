from typing import Optional

import numpy
from PySide6TK.Nodes import FieldDefinition
from PySide6TK.Nodes import FieldType
from PySide6TK.Nodes import PortType

from catena.nodes.generate.generator import GeneratorNode
from catena.nodes.node_processor import ProcessorNode
from catena.preferences import preferences


class GradientProcessor(ProcessorNode):
    """A headless processor that generates a linear gradient between two colors."""

    def __init__(
        self,
        color_a: tuple[int, int, int, int] = (0, 0, 0, 255),
        color_b: tuple[int, int, int, int] = (255, 255, 255, 255),
        angle: float = 0.0,
    ) -> None:
        super().__init__()
        self.color_a = color_a
        self.color_b = color_b
        self.angle = angle

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]] | None = None
    ) -> Optional[numpy.ndarray]:
        """
        Generate a linear gradient between two colors.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Unused; generators
                produce output from parameters only.
        Returns:
            numpy.ndarray | None: A float32 gradient image of shape
                (width, height, 3) with values in [0, 1].
        """
        r_a, g_a, b_a, _ = self.color_a
        r_b, g_b, b_b, _ = self.color_b

        width = preferences.Preferences().general_preferences.texture_resolution
        height = width

        y_idx, x_idx = numpy.indices((height, width), dtype=numpy.float32)

        radians = numpy.deg2rad(self.angle)
        direction_x = numpy.cos(radians)
        direction_y = numpy.sin(radians)

        cx, cy = width / 2.0, height / 2.0
        projection = (x_idx - cx) * direction_x + (y_idx - cy) * direction_y

        max_extent = numpy.sqrt(cx**2 + cy**2)
        t = (projection / max_extent + 1.0) / 2.0
        t = numpy.clip(t, 0.0, 1.0)

        color_a = numpy.array([b_a, g_a, r_a], dtype=numpy.float32) / 255.0
        color_b = numpy.array([b_b, g_b, r_b], dtype=numpy.float32) / 255.0

        result = (
            color_a[None, None, :] * (1 - t[:, :, None])
            + color_b[None, None, :] * t[:, :, None]
        )

        return result.astype(numpy.float32)


class GradientNode(GeneratorNode):
    """A node that generates a linear gradient between two colors."""

    def __init__(self) -> None:
        self._processor = GradientProcessor()
        super().__init__(title="Gradient")

    def _build(self) -> None:
        self.port_out = self.add_port(PortType.OUTPUT, "Output")

        self.add_field(
            FieldDefinition(
                name="color_a",
                label="Color A",
                field_type=FieldType.COLOR,
                default=(0, 0, 0, 255),
            )
        )
        self.add_field(
            FieldDefinition(
                name="color_b",
                label="Color B",
                field_type=FieldType.COLOR,
                default=(255, 255, 255, 255),
            )
        )
        self.add_field(
            FieldDefinition(
                name="angle",
                label="Angle",
                field_type=FieldType.FLOAT,
                default=0.0,
                min_value=-360.0,
                max_value=360.0,
            )
        )

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        self._processor.color_a = self.get_field_value("color_a")
        self._processor.color_b = self.get_field_value("color_b")
        self._processor.angle = self.get_field_value("angle")
        return self._processor.process(inputs)
