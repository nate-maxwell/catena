from typing import Optional

import cv2
import numpy
from PySide6TK.Nodes import FieldDefinition
from PySide6TK.Nodes import FieldType
from PySide6TK.Nodes import PortType

from catena.nodes import data
from catena.nodes.flood_fill import IMAGE_NODE_COLOR
from catena.nodes.node_gui import CatenaNode
from catena.nodes.node_processor import ProcessorNode


class FloodFillProcessor(ProcessorNode):
    """A headless processor that assigns unique random values to each connected region."""

    def __init__(self, threshold: float = 0.5, seed: int = 0) -> None:
        super().__init__()
        self.threshold = threshold
        self.seed = seed

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        """
        Assign a unique random grayscale value to each connected region of
        pixels above the threshold.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Expects key "Input"
                containing a float32 modifier with values in [0, 1].
        Returns:
            numpy.ndarray | None: A float32 modifier of shape (H, W, 3) where
                each connected region has a unique random value in [0, 1],
                and background pixels are black.
        """
        image = inputs.get("Input")
        if image is None:
            return None

        gray = image.mean(axis=2) if image.ndim == 3 else image
        mask = (gray >= self.threshold).astype(numpy.uint8)

        num_labels, labels = cv2.connectedComponents(mask, connectivity=4)

        rng = numpy.random.default_rng(self.seed)
        values = numpy.zeros(num_labels, dtype=numpy.float32)
        values[1:] = rng.random(num_labels - 1).astype(numpy.float32)

        result = values[labels].astype(numpy.float32)

        return numpy.repeat(result[:, :, None], 4, axis=2).astype(numpy.float32)


class FloodFillNode(CatenaNode):
    """A node that assigns unique random values to each connected region."""

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        self._processor = FloodFillProcessor()
        super().__init__(title="Flood Fill")

    def _build(self) -> None:
        self.port_in = self.add_port(PortType.INPUT, "Input")
        self.port_out = self.add_port(
            PortType.OUTPUT, "Output", data.PortDataType.FLOOD_FILL
        )

        self.add_field(
            FieldDefinition(
                name="threshold",
                label="Threshold",
                field_type=FieldType.FLOAT,
                default=0.5,
                min_value=0.0,
                max_value=1.0,
            )
        )
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
        self._processor.threshold = self.get_field_value("threshold")
        self._processor.seed = self.get_field_value("seed")
        return self._processor.process(inputs)
