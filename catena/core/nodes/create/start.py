from PySide6TK.Nodes import PortType

from catena.core.nodes.base import CatenaNode
from catena.core.nodes.create import IMAGE_NODE_COLOR


class StartNode(CatenaNode):

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        super().__init__(title="Start")

    def _build(self) -> None:
        self.port_out = self.add_port(PortType.OUTPUT, "Exec")
