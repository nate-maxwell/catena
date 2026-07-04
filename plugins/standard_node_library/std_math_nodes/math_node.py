from catena import api
from std_math_nodes import IMAGE_NODE_COLOR

_PORT_TYPES = [v for k, v in vars(api.PortDataType).items() if not k.startswith("_")]


class MathNode(api.CatenaNode):
    """A node with dynamic port types for common math operations."""

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self, title: str) -> None:
        super().__init__(title=title)

    def _on_field_changed(self, node: "MathNode") -> None:
        data_type = self.get_field_value("data_type")
        for port in self._ports:
            port.data_type = data_type
            port.set_color(api.DATA_TYPE_COLORS[data_type])

        super()._on_field_changed(node)

    def _build(self) -> None:
        self.add_field(
            api.FieldDefinition(
                name="data_type",
                label="Type",
                field_type=api.FieldType.CHOICE,
                default=api.PortDataType.VECTOR4,
                options=_PORT_TYPES,
            )
        )
