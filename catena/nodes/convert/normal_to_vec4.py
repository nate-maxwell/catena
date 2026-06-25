from typing import Optional

import numpy
from PySide6TK.Nodes import FieldDefinition
from PySide6TK.Nodes import FieldType
from PySide6TK.Nodes import PortType

from catena.nodes.node_gui import CatenaNode
from catena.nodes.convert import IMAGE_NODE_COLOR
from catena.nodes.data import DATA_TYPE_COLORS
from catena.nodes.data import PortDataType
from catena.nodes.node_processor import ProcessorNode


class NormalToVector4Processor(ProcessorNode):
    """
    A headless processor that converts a tangent-space normal map into a
    vector 4 color map.
    """

    def __init__(self) -> None:
        super().__init__()

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        """
        Convert a tangent-space normal map into a height map using
        Frankot-Chellappa gradient integration. The normals encode surface
        slope (X -> dH/dx, Y -> dH/dy), which are unpacked and integrated
        in the Fourier domain to recover the height field.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Expects key "Input"
                containing a float32 normal map in BGR order (B=Z, G=Y, R=X).
        Returns:
            numpy.ndarray | None: A float32 height map of shape (H, W, 3)
                with values in [0, 1].
        """
        image = inputs.get("Input")
        if image is None:
            return None

        return image


class NormalToVector4Node(CatenaNode):
    """A node that converts a tangent-space normal map into a vector 4 color map."""

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        self._processor = NormalToVector4Processor()
        super().__init__(title="Normal to Vec4")

    def _build(self) -> None:
        self.port_in = self.add_port(PortType.INPUT, "Input", PortDataType.NORMAL)
        self.port_in.set_color(DATA_TYPE_COLORS[PortDataType.NORMAL])
        self.port_out = self.add_port(PortType.OUTPUT, "Output")

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        return self._processor.process(inputs)
