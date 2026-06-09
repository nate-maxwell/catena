from PySide6 import QtGui
from PySide6 import QtWidgets

from catena.core.graph.graph_view import GraphView
from catena.core.graph.node import BaseNode
from catena.core.graph.node import FieldDefinition
from catena.core.graph.node import FieldType
from catena.core.graph.port import PortType


class StartNode(BaseNode):

    _COLOR_HEADER = QtGui.QColor(40, 120, 60)

    def __init__(self) -> None:
        super().__init__(title="Start", width=160, body_height=40)

    def _build(self) -> None:
        self.port_out = self.add_port(PortType.OUTPUT, "Exec")


class TransitionNode(BaseNode):

    _COLOR_HEADER = QtGui.QColor(100, 60, 160)

    def __init__(self) -> None:
        super().__init__(title="Transition", width=240, body_height=40)

    def _build(self) -> None:
        self.port_in = self.add_port(PortType.INPUT, "Pane")
        self.port_out = self.add_port(PortType.OUTPUT, "Post Transition")

        self.add_field(
            FieldDefinition(
                name="duration",
                label="Duration",
                field_type=FieldType.FLOAT,
                default=0.5,
                min_value=0.0,
                max_value=10.0,
            )
        )
        self.add_field(
            FieldDefinition(
                name="type",
                label="Type",
                field_type=FieldType.CHOICE,
                default="fade",
                options=["fade", "wipe", "dissolve", "cut"],
            )
        )
        self.add_field(
            FieldDefinition(
                name="easing",
                label="Easing",
                field_type=FieldType.CHOICE,
                default="ease_in_out",
                options=["linear", "ease_in", "ease_out", "ease_in_out"],
            )
        )
        self.add_field(
            FieldDefinition(
                name="color",
                label="Color",
                field_type=FieldType.COLOR,
                default=(0, 0, 0, 255),
            )
        )


class OutroNode(BaseNode):

    _COLOR_HEADER = QtGui.QColor(100, 160, 160)

    def __init__(self) -> None:
        super().__init__(title="Outro", width=160, body_height=40)

    def _build(self) -> None:
        self.port_in = self.add_port(PortType.INPUT, "Pane")


class PanelNode(BaseNode):

    _COLOR_HEADER = QtGui.QColor(160, 60, 60)

    def __init__(self) -> None:
        super().__init__(title="Panel", width=180, body_height=40)

    def _build(self) -> None:
        self.port_in = self.add_port(PortType.INPUT, "Previous")
        self.port_out = self.add_port(PortType.OUTPUT, "Output")

        self.add_field(
            FieldDefinition(
                name="filepath",
                label="Filepath",
                field_type=FieldType.STR,
                default="",
            )
        )
        self.add_field(
            FieldDefinition(
                name="duration",
                label="Duration",
                field_type=FieldType.FLOAT,
                default=3.0,
                min_value=0.0,
                max_value=60.0,
            )
        )
        self.add_field(
            FieldDefinition(
                name="scale",
                label="Scale",
                field_type=FieldType.FLOAT,
                default=1.0,
                min_value=0.1,
                max_value=10.0,
            )
        )
        self.add_field(
            FieldDefinition(
                name="offset",
                label="Offset",
                field_type=FieldType.VEC2,
                default=(0.0, 0.0),
            )
        )
        self.add_field(
            FieldDefinition(
                name="fit_mode",
                label="Fit Mode",
                field_type=FieldType.CHOICE,
                default="Fit",
                options=["Fit", "Fill", "Stretch", "None"],
            )
        )
        self.add_field(
            FieldDefinition(
                name="visible",
                label="Visible",
                field_type=FieldType.BOOL,
                default=True,
            )
        )


class NodeGraphWindow(QtWidgets.QMainWindow):

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Node Graph")
        self.resize(1024, 768)

        self.cur_pos = 0

        self.graph = GraphView(self)
        self.setCentralWidget(self.graph)

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
