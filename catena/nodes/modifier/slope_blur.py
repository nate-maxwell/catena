from typing import Optional

import cv2
import numpy
from PySide6TK.Nodes import FieldDefinition
from PySide6TK.Nodes import FieldType
from PySide6TK.Nodes import PortType

from catena.nodes.node_gui import CatenaNode
from catena.nodes.modifier import IMAGE_NODE_COLOR
from catena.nodes.node_processor import ProcessorNode

_MODES = ["Blur", "Min", "Max"]


class SlopeBlurProcessor(ProcessorNode):
    """A headless processor that blurs an image along per-pixel gradient directions."""

    def __init__(
        self,
        intensity: float = 10.0,
        samples: int = 8,
        mode: str = "Blur",
    ) -> None:
        super().__init__()
        self.intensity = intensity
        self.samples = samples
        self.mode = mode

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        """
        Blur the input image along the per-pixel gradient direction of the
        slope map. Each pixel samples along its own local gradient vector,
        so the blur direction varies across the image.

        Mode controls how samples are combined:
        - Blur: average of all samples (standard blur)
        - Min: minimum of all samples (eats away bright areas)
        - Max: maximum of all samples (smears out bright areas)

        Args:
            inputs (dict[str, numpy.ndarray | None]): Expects keys "Input"
                and "Slope", each a float32 image.
        Returns:
            numpy.ndarray | None: The slope-blurred float32 image.
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
        slope_gray = (
            slope.mean(axis=2) if slope.ndim == 3 else slope.astype(numpy.float32)
        )

        gy, gx = numpy.gradient(slope_gray)
        mag = numpy.sqrt(gx * gx + gy * gy)
        safe_mag = numpy.where(mag < 1e-6, 1.0, mag)
        gx = (gx / safe_mag).astype(numpy.float32)
        gy = (gy / safe_mag).astype(numpy.float32)

        y_idx, x_idx = numpy.indices((height, width), dtype=numpy.float32)
        n = max(2, self.samples)

        if self.mode == "Min":
            accum = numpy.full_like(image, numpy.inf, dtype=numpy.float32)
        elif self.mode == "Max":
            accum = numpy.full_like(image, -numpy.inf, dtype=numpy.float32)
        else:
            accum = numpy.zeros_like(image, dtype=numpy.float32)

        for i in range(n):
            t = (i / (n - 1)) * self.intensity
            map_x = numpy.clip(x_idx + gx * t, 0, width - 1).astype(numpy.float32)
            map_y = numpy.clip(y_idx + gy * t, 0, height - 1).astype(numpy.float32)
            sample = cv2.remap(
                image, map_x, map_y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT
            )

            if self.mode == "Min":
                accum = numpy.minimum(accum, sample)
            elif self.mode == "Max":
                accum = numpy.maximum(accum, sample)
            else:
                accum += sample

        if self.mode == "Blur":
            result = accum / n
        else:
            result = accum

        return numpy.clip(result, 0.0, 1.0).astype(numpy.float32)


class SlopeBlurNode(CatenaNode):
    """A node that blurs an image along the per-pixel gradient of a slope map."""

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
                name="samples",
                label="Samples",
                field_type=FieldType.INT,
                default=8,
                min_value=1,
                max_value=32,
            )
        )
        self.add_field(
            FieldDefinition(
                name="intensity",
                label="Intensity",
                field_type=FieldType.FLOAT,
                default=10.0,
                min_value=0.0,
                max_value=16.0,
            )
        )
        self.add_field(
            FieldDefinition(
                name="mode",
                label="Mode",
                field_type=FieldType.CHOICE,
                default="Blur",
                options=_MODES,
            )
        )

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        self._processor.intensity = self.get_field_value("intensity")
        self._processor.samples = self.get_field_value("samples")
        self._processor.mode = self.get_field_value("mode")
        return self._processor.process(inputs)
