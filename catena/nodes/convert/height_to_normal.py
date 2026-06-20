from typing import Optional

import numpy
from PySide6TK.Nodes import FieldDefinition
from PySide6TK.Nodes import FieldType
from PySide6TK.Nodes import PortType

from catena.nodes.base import CatenaNode
from catena.nodes.convert import IMAGE_NODE_COLOR
from catena.nodes.data import DATA_TYPE_COLORS
from catena.nodes.data import PortDataType
from catena.nodes.processor import ProcessorNode

_SPACES = ["OpenGL", "DirectX"]


class HeightToNormalProcessor(ProcessorNode):
    """A headless processor that converts a height map into a tangent-space normal map."""

    def __init__(self, strength: float = 1.0, space: str = "OpenGL") -> None:
        super().__init__()
        self.strength = strength
        self.space = space

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
        image = inputs.get("Input")
        if image is None:
            return None

        if image.ndim == 3:
            height_field = image.mean(axis=2)
        else:
            height_field = image

        gy, gx = numpy.gradient(height_field)

        nx = -gx * self.strength
        ny = -gy * self.strength
        nz = numpy.ones_like(height_field)

        if self.space == "DirectX":
            ny = -ny

        length = numpy.sqrt(nx * nx + ny * ny + nz * nz)
        nx /= length
        ny /= length
        nz /= length

        nx = (nx + 1.0) * 0.5
        ny = (ny + 1.0) * 0.5
        nz = (nz + 1.0) * 0.5

        return numpy.stack([nz, ny, nx], axis=-1).astype(numpy.float32)


class HeightToNormalNode(CatenaNode):
    """A node that converts a height map into a tangent-space normal map."""

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        self._processor = HeightToNormalProcessor()
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
        self._processor.strength = self.get_field_value("strength")
        self._processor.space = self.get_field_value("space")
        return self._processor.process(inputs)
