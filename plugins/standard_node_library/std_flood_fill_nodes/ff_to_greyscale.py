from typing import Optional

import numpy

from catena import api
from std_flood_fill_nodes import IMAGE_NODE_COLOR


class FloodFillToGreyscaleNode(api.CatenaNode):
    """
    A node that remaps flood fill region values to an even greyscale
    distribution, optionally sampling from a greyscale input.
    """

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        super().__init__(title="Flood Fill to Greyscale")

    def _build(self) -> None:
        self.port_in = self.add_port(
            api.PortType.INPUT, "Flood Fill", api.PortDataType.FLOOD_FILL
        )
        self.port_in_grey = self.add_port(api.PortType.INPUT, "Greyscale")
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
        Remap flood fill region values to an evenly distributed greyscale range,
        optionally sampling values from a greyscale modifier.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Expects key "Input"
                containing a float32 flood fill modifier, and optionally "Greyscale"
                containing a float32 greyscale modifier to sample values from.
        Returns:
            numpy.ndarray | None: A float32 modifier of shape (H, W, 3) where
                each region has a uniformly distributed greyscale value.
        """
        seed = self.get_field_value("seed")
        image = inputs.get("Flood Fill")
        if image is None:
            return None

        greyscale = inputs.get("Greyscale")

        source = image.mean(axis=2) if image.ndim == 3 else image

        quantized = numpy.round(source * 65535).astype(numpy.int32)

        unique_values = numpy.unique(quantized)
        unique_values = unique_values[unique_values > 0]

        if len(unique_values) == 0:
            return numpy.zeros_like(image, dtype=numpy.float32)

        num_regions = len(unique_values)

        if greyscale is not None:
            grey_source = greyscale.mean(axis=2) if greyscale.ndim == 3 else greyscale
            sampled = numpy.array(
                [float(grey_source[quantized == v].mean()) for v in unique_values],
                dtype=numpy.float32,
            )
            value_map = dict(zip(unique_values.tolist(), sampled))
        else:
            rng = numpy.random.default_rng(seed)
            distributed = numpy.linspace(0.0, 1.0, num_regions, dtype=numpy.float32)
            rng.shuffle(distributed)
            value_map = dict(zip(unique_values.tolist(), distributed))

        result = numpy.zeros_like(source, dtype=numpy.float32)
        for v, mapped in value_map.items():
            result[quantized == v] = mapped

        return numpy.repeat(result[:, :, None], 4, axis=2).astype(numpy.float32)
