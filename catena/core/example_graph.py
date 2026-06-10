from PySide6 import QtWidgets
from PySide6TK.Nodes import GraphView

from catena.core.nodes.outro import OutroNode
from catena.core.nodes.panel import PanelNode
from catena.core.nodes.start import StartNode
from catena.core.nodes.transition import TransitionNode


class NodeGraphWindow(QtWidgets.QMainWindow):

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Node Graph")
        self.resize(1024, 768)

        self.cur_pos = 0

        self.graph = GraphView(self)
        self.setCentralWidget(self.graph)

        self._register()
        self._populate()

    def _populate(self) -> None:
        self.node_start = StartNode()
        self.node_pane_a = PanelNode()
        self.node_pane_a.set_field_value(
            "filepath", "T:/git/catena/catena/core/resources/PIC_Example_Board.png"
        )
        self.node_pane_b = PanelNode()
        self.node_transition = TransitionNode()
        self.node_pane_c = PanelNode()
        self.node_outro = OutroNode()

        self.graph.add_node(self.node_start, 0, 0)
        self.graph.add_node(self.node_pane_a, 200, 0)
        self.graph.add_node(self.node_pane_b, 400, 0)
        self.graph.add_node(self.node_transition, 600, 0)
        self.graph.add_node(self.node_pane_c, 900, 0)
        self.graph.add_node(self.node_outro, 1100, 0)

        self.graph.connect_ports(self.node_start.port_out, self.node_pane_a.port_in)
        self.graph.connect_ports(self.node_pane_a.port_out, self.node_pane_b.port_in)
        self.graph.connect_ports(
            self.node_pane_b.port_out, self.node_transition.port_in
        )
        self.graph.connect_ports(
            self.node_transition.port_out, self.node_pane_c.port_in
        )
        self.graph.connect_ports(self.node_pane_c.port_out, self.node_outro.port_in)

    def _register(self) -> None:
        self.graph.register_node("Main", PanelNode)
        self.graph.register_node("Main", TransitionNode)
        self.graph.register_node("Main", StartNode)
        self.graph.register_node("Main", OutroNode)
