from typing import Optional

import numpy
from PySide6TK.Nodes.node import PortType

from catena.core.nodes.base import CatenaNode
from catena.core.nodes.misc import IMAGE_NODE_COLOR


class RerouteNode(CatenaNode):
    """A do-nothing node meant simply to let users route wires more freely."""

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        self._HEADER_HEIGHT = 5
        super().__init__(title="", width=20, body_height=20)

    def _build(self) -> None:
        self.port_in = self.add_port(PortType.INPUT, "")
        self.port_out = self.add_port(PortType.OUTPUT, "")

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        return inputs.get("")
