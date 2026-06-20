from typing import Optional

import numpy
from PySide6TK.Nodes import FieldDefinition
from PySide6TK.Nodes import FieldType
from PySide6TK.Nodes import PortType

from catena.nodes.node_gui import CatenaNode
from catena.nodes.node_processor import ProcessorNode
from catena.nodes.image import IMAGE_NODE_COLOR


class HistogramScanProcessor(ProcessorNode):
    """
    A headless processor that isolates a band of luminance values from a
    height map, outputting white where pixels fall within the band and
    black elsewhere.
    """

    def __init__(self, position: float = 0.5, contrast: float = 0.5) -> None:
        super().__init__()
        self.position = position
        self.contrast = contrast

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        """
        Isolate a band of luminance values centered on position with width
        controlled by contrast.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Expects key "Input"
                containing a float32 height map with values in [0, 1].
        Returns:
            numpy.ndarray | None: A float32 mask image with values in [0, 1]
                where pixels within the selected height band are white.
        """
        image = inputs.get("Input")
        if image is None:
            return None

        luminance = image.mean(axis=2) if image.ndim == 3 else image

        half_width = (1.0 - self.contrast) * 0.5
        low = self.position - half_width
        high = self.position + half_width

        epsilon = 1e-6
        low_fade = numpy.clip((luminance - low) / (half_width + epsilon), 0.0, 1.0)
        high_fade = numpy.clip((high - luminance) / (half_width + epsilon), 0.0, 1.0)
        mask = numpy.minimum(low_fade, high_fade).astype(numpy.float32)

        return numpy.repeat(mask[:, :, None], 3, axis=2).astype(numpy.float32)


class HistogramScanNode(CatenaNode):
    """
    A node that isolates a band of height values from a height map,
    outputting a white mask where pixels fall within the selected range.
    """

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        self._processor = HistogramScanProcessor()
        super().__init__(title="Histogram Scan")

    def _build(self) -> None:
        self.port_in = self.add_port(PortType.INPUT, "Input")
        self.port_out = self.add_port(PortType.OUTPUT, "Output")

        self.add_field(
            FieldDefinition(
                name="position",
                label="Position",
                field_type=FieldType.FLOAT,
                default=0.5,
                min_value=0.0,
                max_value=1.0,
            )
        )
        self.add_field(
            FieldDefinition(
                name="contrast",
                label="Contrast",
                field_type=FieldType.FLOAT,
                default=0.5,
                min_value=0.0,
                max_value=1.0,
            )
        )

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        self._processor.position = self.get_field_value("position")
        self._processor.contrast = self.get_field_value("contrast")
        return self._processor.process(inputs)
