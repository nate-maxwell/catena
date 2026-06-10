from PySide6 import QtGui
from PySide6TK.Nodes import PortType

from catena.core.nodes.base import CatenaNode


class OutroNode(CatenaNode):

    _COLOR_HEADER = QtGui.QColor(100, 160, 160)

    def __init__(self) -> None:
        super().__init__(title="Outro", width=160, body_height=40)

    def _build(self) -> None:
        self.port_in = self.add_port(PortType.INPUT, "Pane")
