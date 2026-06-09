import sys

from PySide6 import QtGui
from PySide6 import QtWidgets

from catena.core.graph.graph_view import GraphView
from catena.core.graph.node import BaseNode
from catena.core.graph.port import PortType


class InputNode(BaseNode):

    _COLOR_HEADER = QtGui.QColor(40, 120, 60)

    def __init__(self, title: str) -> None:
        super().__init__(title=title, width=160, body_height=40)

    def _build(self) -> None:
        self.port_out = self.add_port(PortType.OUTPUT, "value")


class MathNode(BaseNode):

    _COLOR_HEADER = QtGui.QColor(100, 60, 160)

    def __init__(self, operation: str) -> None:
        super().__init__(title=operation, width=180, body_height=60)

    def _build(self) -> None:
        self.port_a = self.add_port(PortType.INPUT, "A")
        self.port_b = self.add_port(PortType.INPUT, "B")
        self.port_out = self.add_port(PortType.OUTPUT, "result")


class OutputNode(BaseNode):

    _COLOR_HEADER = QtGui.QColor(160, 60, 60)

    def __init__(self) -> None:
        super().__init__(title="Output", width=160, body_height=40)

    def _build(self) -> None:
        self.port_in = self.add_port(PortType.INPUT, "value")


class NodeGraphWindow(QtWidgets.QMainWindow):

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Node Graph")
        self.resize(1024, 768)

        self.graph = GraphView(self)
        self.setCentralWidget(self.graph)

        self._populate()

    def _populate(self) -> None:
        self.node_a = InputNode("Input A")
        self.node_b = InputNode("Input B")
        self.node_multiply = MathNode("Multiply")
        self.node_output = OutputNode()

        self.graph.add_node(self.node_a, -320, -80)
        self.graph.add_node(self.node_b, -320, 60)
        self.graph.add_node(self.node_multiply, -80, -20)
        self.graph.add_node(self.node_output, 180, -20)

        self.graph.connect_ports(self.node_a.port_out, self.node_multiply.port_a)
        self.graph.connect_ports(self.node_b.port_out, self.node_multiply.port_b)
        self.graph.connect_ports(self.node_multiply.port_out, self.node_output.port_in)


def main() -> int:
    app = QtWidgets.QApplication(sys.argv)
    window = NodeGraphWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
