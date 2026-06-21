from typing import Optional

import numpy
from PySide6TK.Nodes import FieldDefinition
from PySide6TK.Nodes import FieldType
from PySide6TK.Nodes import PortType

from catena.nodes.node_gui import CatenaNode
from catena.nodes.node_processor import ProcessorNode
from catena.nodes.flood_fill import IMAGE_NODE_COLOR
from catena.nodes import data


class FloodFillToRandomColorProcessor(ProcessorNode):
    """A headless processor that assigns a unique random color to each flood fill region."""

    def __init__(self, seed: int = 0) -> None:
        super().__init__()
        self.seed = seed

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        """
        Assign a unique random BGR color to each connected region in a
        flood fill image.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Expects key "Flood Fill"
                containing a float32 flood fill image.
        Returns:
            numpy.ndarray | None: A float32 image of shape (H, W, 3) with
                values in [0, 1] where each region has a unique random color.
        """
        image = inputs.get("Flood Fill")
        if image is None:
            return None

        source = image.mean(axis=2) if image.ndim == 3 else image
        quantized = numpy.round(source * 65535).astype(numpy.int32)

        unique_values = numpy.unique(quantized)
        unique_values = unique_values[unique_values > 0]

        if len(unique_values) == 0:
            return numpy.zeros((*source.shape, 3), dtype=numpy.float32)

        rng = numpy.random.default_rng(self.seed)
        colors = rng.random((len(unique_values), 3)).astype(numpy.float32)
        color_map = dict(zip(unique_values.tolist(), colors))

        height, width = source.shape[:2]
        result = numpy.zeros((height, width, 3), dtype=numpy.float32)

        for v, color in color_map.items():
            mask = quantized == v
            result[mask] = color

        return result


class FloodFillToRandomColorNode(CatenaNode):
    """A node that assigns a unique random color to each flood fill region."""

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        self._processor = FloodFillToRandomColorProcessor()
        super().__init__(title="Flood Fill to Random Color")

    def _build(self) -> None:
        self.port_in = self.add_port(
            PortType.INPUT, "Flood Fill", data.PortDataType.FLOOD_FILL
        )
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

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        self._processor.seed = self.get_field_value("seed")
        return self._processor.process(inputs)
