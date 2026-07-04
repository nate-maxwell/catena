from typing import Optional

import numpy

from catena import api
from std_flood_fill_nodes import IMAGE_NODE_COLOR


class FloodFillToGradientNode(api.CatenaNode):
    """
    A node that assigns a directional gradient to each connected region
    in a flood fill modifier.
    """

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        super().__init__(title="Flood Fill to Gradient")

    def _build(self) -> None:
        self.port_in = self.add_port(
            api.PortType.INPUT, "Flood Fill", api.PortDataType.FLOOD_FILL
        )
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
        self.add_field(
            api.FieldDefinition(
                name="direction_seed",
                label="Direction Seed",
                field_type=api.FieldType.FLOAT,
                default=1.0,
                min_value=0.0,
                max_value=999999.0,
            )
        )

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        """
        Assign a gradient spanning each flood fill region, with a random
        direction per region controlled by direction_randomness.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Expects key "Flood Fill"
                containing a float32 flood fill modifier.
        Returns:
            numpy.ndarray | None: A float32 modifier of shape (H, W, 3) where
                each region is filled with a gradient spanning its bounds.
        """
        seed = self.get_field_value("seed")
        direction_randomness = self.get_field_value("direction_seed")
        image = inputs.get("Flood Fill")
        if image is None:
            return None

        source = image.mean(axis=2) if image.ndim == 3 else image
        quantized = numpy.round(source * 65535).astype(numpy.int32)

        unique_values = numpy.unique(quantized)
        unique_values = unique_values[unique_values > 0]

        if len(unique_values) == 0:
            return numpy.zeros_like(image, dtype=numpy.float32)

        rng = numpy.random.default_rng(seed)
        angles = rng.uniform(0.0, 360.0 * direction_randomness, len(unique_values))

        height, width = source.shape[:2]
        y_idx, x_idx = numpy.indices((height, width), dtype=numpy.float32)

        result = numpy.zeros((height, width), dtype=numpy.float32)

        for i, v in enumerate(unique_values):
            mask = quantized == v

            ys = y_idx[mask]
            xs = x_idx[mask]

            radians = numpy.deg2rad(angles[i])
            cos_a = numpy.cos(radians)
            sin_a = numpy.sin(radians)

            projection = xs * cos_a + ys * sin_a

            proj_min = projection.min()
            proj_max = projection.max()
            proj_range = proj_max - proj_min

            if proj_range < 1e-6:
                result[mask] = 0.5
            else:
                full_projection = x_idx * cos_a + y_idx * sin_a
                normalized = (full_projection[mask] - proj_min) / proj_range
                result[mask] = numpy.clip(normalized, 0.0, 1.0)

        return numpy.repeat(result[:, :, None], 4, axis=2).astype(numpy.float32)
