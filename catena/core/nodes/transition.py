from PySide6 import QtGui
from PySide6TK.Nodes import FieldDefinition
from PySide6TK.Nodes import FieldType
from PySide6TK.Nodes import PortType

from catena.core.nodes.base import CatenaNode


class TransitionNode(CatenaNode):

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
