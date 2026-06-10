from PySide6 import QtGui
from PySide6TK.Nodes import FieldDefinition
from PySide6TK.Nodes import FieldType
from PySide6TK.Nodes import PortType

from catena.core.nodes.base import CatenaNode


class PanelNode(CatenaNode):

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
