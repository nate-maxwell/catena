from typing import Optional

import cv2
import numpy

from catena import api
from std_transform_nodes import IMAGE_NODE_COLOR


class WarpNode(api.CatenaNode):
    """A node that displaces pixels in a direction, scaled by a displacement map."""

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:

        super().__init__(title="Warp")

    def _build(self) -> None:
        self.port_in = self.add_port(api.PortType.INPUT, "Input")
        self.port_in_displacement = self.add_port(api.PortType.INPUT, "Displacement")
        self.port_out = self.add_port(api.PortType.OUTPUT, "Output")

        self.add_field(
            api.FieldDefinition(
                name="strength",
                label="Strength",
                field_type=api.FieldType.FLOAT,
                default=10.0,
                min_value=0.0,
                max_value=10000.0,
            )
        )
        self.add_field(
            api.FieldDefinition(
                name="direction",
                label="Direction",
                field_type=api.FieldType.FLOAT,
                default=0.0,
                min_value=-360.0,
                max_value=360.0,
            )
        )

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        """
        Displace pixels in a fixed direction, scaled by a displacement map.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Expects keys "Input"
                and optionally "Displacement", each containing a float32 modifier.
                If Displacement is None, a uniform full-modifier displacement is applied.
        Returns:
            numpy.ndarray | None: The warped float32 modifier, or the unmodified
                input if strength is zero or no input is provided.
        """
        strength = self.get_field_value("strength")
        direction = self.get_field_value("direction")
        image = inputs.get("Input")
        displacement = inputs.get("Displacement")

        if image is None:
            return None

        if strength <= 0:
            return image

        height, width = image.shape[:2]

        if displacement is None:
            disp = numpy.ones((height, width), dtype=numpy.float32)
        else:
            if displacement.shape[:2] != (height, width):
                displacement = cv2.resize(displacement, (width, height))
            if displacement.ndim == 3:
                disp = displacement.mean(axis=2)
            else:
                disp = displacement.astype(numpy.float32)

        radians = numpy.deg2rad(direction)
        direction_x = numpy.cos(radians)
        direction_y = numpy.sin(radians)

        offset_x = disp * direction_x * strength
        offset_y = disp * direction_y * strength

        y_idx, x_idx = numpy.indices((height, width), dtype=numpy.float32)
        map_x = (x_idx + offset_x).astype(numpy.float32)
        map_y = (y_idx + offset_y).astype(numpy.float32)

        result = cv2.remap(
            image,
            map_x,
            map_y,
            interpolation=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_REFLECT,
        )
        return result.astype(numpy.float32)
