from typing import Optional

import numpy
from PySide6TK.Nodes import FieldDefinition
from PySide6TK.Nodes import FieldType
from PySide6TK.Nodes import PortType

from catena.nodes.node_gui import CatenaNode
from catena.nodes.math import IMAGE_NODE_COLOR
from catena.nodes.node_processor import ProcessorNode


class ArctangentProcessor(ProcessorNode):
    """A headless processor that applies an arctangent remap or generates a directional wave."""

    def __init__(
        self,
        frequency: float = 8.0,
        phase: float = 0.0,
        angle: float = 0.0,
        scale: float = 1.0,
    ) -> None:
        super().__init__()
        self.frequency = frequency
        self.phase = phase
        self.angle = angle
        self.scale = scale

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        """
        Apply an arctangent remap to an input modifier, or generate a directional
        arctangent wave if no input is connected.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Optionally expects key
                "Input" containing a float32 modifier. If None, generates a
                directional wave pattern.
        Returns:
            numpy.ndarray | None: A float32 modifier of shape (H, W, 3) with
                values in [0, 1].
        """
        image = inputs.get("Input")

        width, height = 512, 512
        if image is not None:
            height, width = image.shape[:2]

        if image is None:
            y_idx, x_idx = numpy.indices((height, width), dtype=numpy.float32)
            radians = numpy.deg2rad(self.angle)
            direction_x = numpy.cos(radians)
            direction_y = numpy.sin(radians)

            cx, cy = width / 2.0, height / 2.0
            projection = (x_idx - cx) * direction_x + (y_idx - cy) * direction_y
            max_extent = max(width, height)

            phase_rad = numpy.deg2rad(self.phase)
            wave = numpy.arctan(
                (2 * self.frequency * projection / max_extent + phase_rad) * self.scale
            )
            wave = (wave / (numpy.pi / 2.0) + 1.0) * 0.5

            return numpy.repeat(wave[:, :, None], 3, axis=2).astype(numpy.float32)

        gray = image.mean(axis=2)
        phase_rad = numpy.deg2rad(self.phase)
        centered = (gray - 0.5) * 2.0
        wave = numpy.arctan((self.frequency * centered + phase_rad) * self.scale)
        wave = (wave / (numpy.pi / 2.0) + 1.0) * 0.5

        return numpy.repeat(wave[:, :, None], 3, axis=2).astype(numpy.float32)


class ArctangentNode(CatenaNode):
    """A node that applies an arctangent remap, either as a generator or as a remap of an input."""

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        self._processor = ArctangentProcessor()
        super().__init__(title="Arctangent")

    def _build(self) -> None:
        self.port_in = self.add_port(PortType.INPUT, "Input")
        self.port_out = self.add_port(PortType.OUTPUT, "Output")

        self.add_field(
            FieldDefinition(
                name="frequency",
                label="Frequency",
                field_type=FieldType.FLOAT,
                default=8.0,
                min_value=0.1,
                max_value=64.0,
            )
        )
        self.add_field(
            FieldDefinition(
                name="phase",
                label="Phase",
                field_type=FieldType.FLOAT,
                default=0.0,
                min_value=-360.0,
                max_value=360.0,
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
        self.add_field(
            FieldDefinition(
                name="scale",
                label="Scale",
                field_type=FieldType.FLOAT,
                default=1.0,
                min_value=0.01,
                max_value=20.0,
            )
        )

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        self._processor.frequency = self.get_field_value("frequency")
        self._processor.phase = self.get_field_value("phase")
        self._processor.angle = self.get_field_value("angle")
        self._processor.scale = self.get_field_value("scale")
        return self._processor.process(inputs)
