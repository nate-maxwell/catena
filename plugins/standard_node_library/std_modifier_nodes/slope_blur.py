from typing import Optional

import cv2
import numpy


from catena import api
from std_modifier_nodes import IMAGE_NODE_COLOR

_MODES = ["Blur", "Min", "Max"]


class SlopeBlurNode(api.CatenaNode):
    """A node that blurs an image along the per-pixel gradient of a slope map."""

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:

        super().__init__(title="Slope Blur")

    def _build(self) -> None:
        self.port_in = self.add_port(api.PortType.INPUT, "Input")
        self.port_in_slope = self.add_port(api.PortType.INPUT, "Slope")
        self.port_out = self.add_port(api.PortType.OUTPUT, "Output")

        self.add_field(
            api.FieldDefinition(
                name="samples",
                label="Samples",
                field_type=api.FieldType.INT,
                default=8,
                min_value=1,
                max_value=32,
            )
        )
        self.add_field(
            api.FieldDefinition(
                name="intensity",
                label="Intensity",
                field_type=api.FieldType.FLOAT,
                default=10.0,
                min_value=0.0,
                max_value=999999.0,
            )
        )
        self.add_field(
            api.FieldDefinition(
                name="mode",
                label="Mode",
                field_type=api.FieldType.CHOICE,
                default="Blur",
                options=_MODES,
            )
        )

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
        intensity = self.get_field_value("intensity")
        samples = self.get_field_value("samples")
        mode = self.get_field_value("mode")

        image = inputs.get("Input")
        slope = inputs.get("Slope")

        if image is None:
            return None

        if intensity <= 0 or slope is None:
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
        n = max(2, samples)

        if mode == "Min":
            accum = numpy.full_like(image, numpy.inf, dtype=numpy.float32)
        elif mode == "Max":
            accum = numpy.full_like(image, -numpy.inf, dtype=numpy.float32)
        else:
            accum = numpy.zeros_like(image, dtype=numpy.float32)

        for i in range(n):
            t = (i / (n - 1)) * intensity
            map_x = numpy.clip(x_idx + gx * t, 0, width - 1).astype(numpy.float32)
            map_y = numpy.clip(y_idx + gy * t, 0, height - 1).astype(numpy.float32)
            sample = cv2.remap(
                image, map_x, map_y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT
            )

            if mode == "Min":
                accum = numpy.minimum(accum, sample)
            elif mode == "Max":
                accum = numpy.maximum(accum, sample)
            else:
                accum += sample

        if mode == "Blur":
            result = accum / n
        else:
            result = accum

        return numpy.clip(result, 0.0, 1.0).astype(numpy.float32)
