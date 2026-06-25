from typing import Optional

import cv2
import numpy
from PySide6TK.Nodes import FieldDefinition
from PySide6TK.Nodes import FieldType
from PySide6TK.Nodes import PortType

from catena.nodes.node_gui import CatenaNode
from catena.nodes.modifier import IMAGE_NODE_COLOR
from catena.nodes.node_processor import ProcessorNode


class SlopeBlurProcessor(ProcessorNode):
    """A headless processor that blurs an modifier along the gradient of a slope map."""

    def __init__(self, intensity: float = 10.0, samples: int = 8) -> None:
        super().__init__()
        self.intensity = intensity
        self.samples = samples

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        """
        Blur an modifier along the gradient direction of a slope/height map.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Expects keys "Input"
                and "Slope", each containing a float32 modifier.
        Returns:
            numpy.ndarray | None: The slope-blurred float32 modifier, or the
                unmodified input if Slope is None or intensity is zero.
        """
        image = inputs.get("Input")
        slope = inputs.get("Slope")

        if image is None:
            return None

        if self.intensity <= 0 or slope is None:
            return image

        height, width = image.shape[:2]

        if slope.shape[:2] != (height, width):
            slope = cv2.resize(slope, (width, height))

        if slope.ndim == 3:
            slope_gray = slope.mean(axis=2)
        else:
            slope_gray = slope

        gy, gx = numpy.gradient(slope_gray)

        grad_max = max(numpy.abs(gx).max(), numpy.abs(gy).max(), 1e-6)
        gx = gx / grad_max
        gy = gy / grad_max

        y_idx, x_idx = numpy.indices((height, width), dtype=numpy.float32)

        accum = numpy.zeros_like(image, dtype=numpy.float32)

        for i in range(self.samples):
            t = (i / max(self.samples - 1, 1)) - 0.5

            map_x = (x_idx + gx * self.intensity * t).astype(numpy.float32)
            map_y = (y_idx + gy * self.intensity * t).astype(numpy.float32)

            sample = cv2.remap(
                image,
                map_x,
                map_y,
                interpolation=cv2.INTER_LINEAR,
                borderMode=cv2.BORDER_REFLECT,
            )
            accum += sample

        return (accum / self.samples).astype(numpy.float32)


class SlopeBlurNode(CatenaNode):
    """A node that blurs an modifier along the gradient of a slope/height map."""

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        self._processor = SlopeBlurProcessor()
        super().__init__(title="Slope Blur")

    def _build(self) -> None:
        self.port_in = self.add_port(PortType.INPUT, "Input")
        self.port_in_slope = self.add_port(PortType.INPUT, "Slope")
        self.port_out = self.add_port(PortType.OUTPUT, "Output")

        self.add_field(
            FieldDefinition(
                name="intensity",
                label="Intensity",
                field_type=FieldType.FLOAT,
                default=10.0,
                min_value=0.0,
                max_value=999999.0,
            )
        )
        self.add_field(
            FieldDefinition(
                name="samples",
                label="Samples",
                field_type=FieldType.INT,
                default=8,
                min_value=1,
                max_value=32,
            )
        )

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        self._processor.intensity = self.get_field_value("intensity")
        self._processor.samples = self.get_field_value("samples")
        return self._processor.process(inputs)
