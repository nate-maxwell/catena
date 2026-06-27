from typing import Optional

import numpy

from catena import api
from std_convert_nodes import IMAGE_NODE_COLOR

_SPACES = ["OpenGL", "DirectX"]


class HeightToNormalNode(api.CatenaNode):
    """A node that converts a height map into a tangent-space normal map."""

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        super().__init__(title="Height to Normal")

    def _build(self) -> None:
        self.port_in = self.add_port(api.PortType.INPUT, "Input")
        self.port_out = self.add_port(
            api.PortType.OUTPUT, "Output", api.PortDataType.NORMAL
        )
        self.port_out.set_color(api.DATA_TYPE_COLORS[api.PortDataType.NORMAL])

        self.add_field(
            api.FieldDefinition(
                name="strength",
                label="Strength",
                field_type=api.FieldType.FLOAT,
                default=1.0,
                min_value=0.01,
                max_value=10.0,
            )
        )
        self.add_field(
            api.FieldDefinition(
                name="space",
                label="Space",
                field_type=api.FieldType.CHOICE,
                default="OpenGL",
                options=_SPACES,
            )
        )

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        """
        Convert a height map into a tangent-space normal map.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Expects key "Input"
                containing a float32 height map.
        Returns:
            numpy.ndarray | None: A float32 normal map of shape (H, W, 3)
                in BGR order (B=Z, G=Y, R=X) with values in [0, 1].
        """
        strength = self.get_field_value("strength")
        space = self.get_field_value("space")
        image = inputs.get("Input")
        if image is None:
            return None

        if image.ndim == 3:
            height_field = image.mean(axis=2)
        else:
            height_field = image

        gy, gx = numpy.gradient(height_field)

        nx = -gx * strength
        ny = -gy * strength
        nz = numpy.ones_like(height_field)

        if space == "DirectX":
            ny = -ny

        length = numpy.sqrt(nx * nx + ny * ny + nz * nz)
        nx /= length
        ny /= length
        nz /= length

        nx = (nx + 1.0) * 0.5
        ny = (ny + 1.0) * 0.5
        nz = (nz + 1.0) * 0.5

        return numpy.stack([nz, ny, nx], axis=-1).astype(numpy.float32)
