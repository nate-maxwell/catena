from typing import Optional

import cv2
import numpy
from PySide6 import QtGui
from PySide6TK.Nodes.node import FieldDefinition
from PySide6TK.Nodes.node import FieldType
from PySide6TK.Nodes.node import PortType

from catena.core.nodes.base import CatenaNode
from catena.core.nodes.convert import IMAGE_NODE_COLOR


class HeightToAONode(CatenaNode):
    """A node that approximates ambient occlusion from a height map."""

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        super().__init__(title="Height to AO")

    def _build(self) -> None:
        self.port_in = self.add_port(PortType.INPUT, "Input")
        self.port_out = self.add_port(PortType.OUTPUT, "Output")

        self.add_field(
            FieldDefinition(
                name="strength",
                label="Strength",
                field_type=FieldType.FLOAT,
                default=1.0,
                min_value=0.01,
                max_value=10.0,
            )
        )
        self.add_field(
            FieldDefinition(
                name="samples",
                label="Samples",
                field_type=FieldType.INT,
                default=4,
                min_value=1,
                max_value=8,
            )
        )

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        image = inputs.get("Input")
        if image is None:
            return None

        strength = self.get_field_value("strength")
        samples = self.get_field_value("samples")

        if image.ndim == 3:
            height_field = image.mean(axis=2)
        else:
            height_field = image

        occlusion = numpy.zeros_like(height_field, dtype=numpy.float32)
        total_weight = 0.0

        for i in range(samples):
            radius = 2 ** (i + 1)
            kernel_size = radius * 2 + 1

            blurred = cv2.blur(height_field, (kernel_size, kernel_size))

            diff = blurred - height_field
            diff = numpy.clip(diff, 0.0, 1.0)

            weight = 1.0 / radius
            occlusion += diff * weight
            total_weight += weight

        occlusion /= total_weight
        occlusion *= strength

        ao = 1.0 - numpy.clip(occlusion, 0.0, 1.0)

        result = numpy.repeat(ao[:, :, None], 3, axis=2).astype(numpy.float32)
        return result
