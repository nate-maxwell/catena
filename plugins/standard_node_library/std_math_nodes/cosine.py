from typing import Optional

import numpy

from catena import api
from std_math_nodes import IMAGE_NODE_COLOR


class CosineNode(api.CatenaNode):
    """
    A node that applies a cosine wave, either as a generator or as a remap of
    an input.
    """

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        super().__init__(title="Cosine")

    def _build(self) -> None:
        self.port_in = self.add_port(api.PortType.INPUT, "Input")
        self.port_out = self.add_port(api.PortType.OUTPUT, "Output")

        self.add_field(
            api.FieldDefinition(
                name="frequency",
                label="Frequency",
                field_type=api.FieldType.FLOAT,
                default=8.0,
                min_value=0.1,
                max_value=64.0,
            )
        )
        self.add_field(
            api.FieldDefinition(
                name="phase",
                label="Phase",
                field_type=api.FieldType.FLOAT,
                default=0.0,
                min_value=-360.0,
                max_value=360.0,
            )
        )
        self.add_field(
            api.FieldDefinition(
                name="angle",
                label="Angle",
                field_type=api.FieldType.FLOAT,
                default=0.0,
                min_value=-360.0,
                max_value=360.0,
            )
        )

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        """
        Apply a cosine wave remap to an input modifier, or generate a directional
        cosine wave if no input is connected.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Optionally expects key
                "Input" containing a float32 modifier. If None, generates a
                directional wave pattern.
        Returns:
            numpy.ndarray | None: A float32 modifier of shape (H, W, 3) with
                values in [0, 1].
        """
        frequency = self.get_field_value("frequency")
        phase = self.get_field_value("phase")
        angle = self.get_field_value("angle")
        image = inputs.get("Input")

        width, height = api.get_texture_resolution()
        if image is not None:
            height, width = image.shape[:2]

        if image is None:
            y_idx, x_idx = numpy.indices((height, width), dtype=numpy.float32)
            radians = numpy.deg2rad(angle)
            direction_x = numpy.cos(radians)
            direction_y = numpy.sin(radians)

            cx, cy = width / 2.0, height / 2.0
            projection = (x_idx - cx) * direction_x + (y_idx - cy) * direction_y
            max_extent = max(width, height)

            phase_rad = numpy.deg2rad(phase)
            wave = numpy.cos(
                2 * numpy.pi * frequency * projection / max_extent + phase_rad
            )
            wave = (wave + 1.0) * 0.5

            return numpy.repeat(wave[:, :, None], 3, axis=2).astype(numpy.float32)

        gray = image.mean(axis=2)
        phase_rad = numpy.deg2rad(phase)
        wave = numpy.cos(2 * numpy.pi * frequency * gray + phase_rad)
        wave = (wave + 1.0) * 0.5

        return numpy.repeat(wave[:, :, None], 3, axis=2).astype(numpy.float32)
