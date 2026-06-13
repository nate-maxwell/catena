from PySide6 import QtGui
from PySide6TK.Nodes import PortType

from catena.core.nodes.base import CatenaNode


class StartNode(CatenaNode):

    _COLOR_HEADER = QtGui.QColor(40, 120, 60)

    def __init__(self) -> None:
        super().__init__(title="Start", width=160, body_height=40)

    def _build(self) -> None:
        self.port_out = self.add_port(PortType.OUTPUT, "Exec")
