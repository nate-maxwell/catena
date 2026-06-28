from typing import Optional

import numpy

from catena import api
from std_flood_fill_nodes import IMAGE_NODE_COLOR


class FloodFillToRandomColorNode(api.CatenaNode):
    """A node that assigns a unique random color to each flood fill region."""

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        super().__init__(title="Flood Fill to Random Color")

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

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        """
        Assign a unique random BGR color to each connected region in a
        flood fill modifier.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Expects key "Flood Fill"
                containing a float32 flood fill modifier.
        Returns:
            numpy.ndarray | None: A float32 modifier of shape (H, W, 3) with
                values in [0, 1] where each region has a unique random color.
        """
        seed = self.get_field_value("seed")
        image = inputs.get("Flood Fill")
        if image is None:
            return None

        source = image.mean(axis=2) if image.ndim == 3 else image
        quantized = numpy.round(source * 65535).astype(numpy.int32)

        unique_values = numpy.unique(quantized)
        unique_values = unique_values[unique_values > 0]

        if len(unique_values) == 0:
            return numpy.zeros((*source.shape, 4), dtype=numpy.float32)

        rng = numpy.random.default_rng(seed)
        colors = rng.random((len(unique_values), 4)).astype(numpy.float32)
        color_map = dict(zip(unique_values.tolist(), colors))

        height, width = source.shape[:2]
        result = numpy.zeros((height, width, 4), dtype=numpy.float32)

        for v, color in color_map.items():
            mask = quantized == v
            result[mask] = color

        return result
