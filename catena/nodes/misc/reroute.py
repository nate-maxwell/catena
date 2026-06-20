from typing import Optional

import numpy
from PySide6TK.Nodes import PortType

from catena.nodes.node_gui import CatenaNode
from catena.nodes.misc import IMAGE_NODE_COLOR
from catena.nodes.node_processor import ProcessorNode


class RerouteProcessor(ProcessorNode):
    """A pass-through processor that forwards its input unchanged."""

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        return inputs.get("")


class RerouteNode(CatenaNode):
    """A do-nothing node meant simply to let users route wires more freely."""

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        self._HEADER_HEIGHT = 5
        super().__init__(title="", width=20, body_height=20)
        self._processor = RerouteProcessor()

    def _build(self) -> None:
        self.port_in = self.add_port(PortType.INPUT, "")
        self.port_out = self.add_port(PortType.OUTPUT, "")

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        return self._processor.process(inputs)
