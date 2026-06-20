from typing import Optional

import numpy
from PySide6TK.Nodes import FieldDefinition
from PySide6TK.Nodes import FieldType
from PySide6TK.Nodes import PortType

from catena.application.nodes.base import CatenaNode
from catena.application.nodes.data import DATA_TYPE_COLORS
from catena.application.nodes.data import PortDataType
from catena.application.nodes.convert import IMAGE_NODE_COLOR

_SPACES = ["OpenGL", "DirectX"]


class HeightToNormalNode(CatenaNode):
    """A node that converts a height map into a tangent-space normal map."""

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        super().__init__(title="Height to Normal")

    def _build(self) -> None:
        self.port_in = self.add_port(PortType.INPUT, "Input")
        self.port_out = self.add_port(PortType.OUTPUT, "Output", PortDataType.NORMAL)
        self.port_out.set_color(DATA_TYPE_COLORS[PortDataType.NORMAL])

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
                name="space",
                label="Space",
                field_type=FieldType.CHOICE,
                default="OpenGL",
                options=_SPACES,
            )
        )

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        image = inputs.get("Input")
        if image is None:
            return None

        strength = self.get_field_value("strength")
        space = self.get_field_value("space")

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

        result = numpy.stack([nz, ny, nx], axis=-1).astype(numpy.float32)
        return result
