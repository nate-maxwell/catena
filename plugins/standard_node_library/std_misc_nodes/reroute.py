from typing import Optional

import numpy

from catena import api
from std_misc_nodes import IMAGE_NODE_COLOR


class RerouteNode(api.CatenaNode):
    """A do-nothing node meant simply to let users route wires more freely."""

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        self._HEADER_HEIGHT = 5
        super().__init__(title="", width=20, body_height=20)
        self._processor = RerouteProcessor()

    def _build(self) -> None:
        self.port_in = self.add_port(api.PortType.INPUT, "")
        self.port_out = self.add_port(api.PortType.OUTPUT, "")

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        return inputs.get("")
