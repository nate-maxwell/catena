from catena import api
from std_graph_nodes import IMAGE_NODE_COLOR

_PORT_TYPES = [v for k, v in vars(api.PortDataType).items() if not k.startswith("_")]


class GraphOutputNode(api.CatenaNode):
    """
    A node that defines a named output port for a subgraph.
    Appears as an output port on the SubgraphNode in the outer graph.
    """

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        super().__init__(title="Graph Output", width=140, body_height=20)

    def _build(self) -> None:
        self.port_in = self.add_port(
            api.PortType.INPUT, "Input", api.PortDataType.VECTOR4
        )

        self.add_field(
            api.FieldDefinition(
                name="name",
                label="Name",
                field_type=api.FieldType.STR,
                default="Output",
            )
        )
        self.add_field(
            api.FieldDefinition(
                name="data_type",
                label="Type",
                field_type=api.FieldType.CHOICE,
                default=api.PortDataType.VECTOR4,
                options=_PORT_TYPES,
            )
        )
        self._sync_port_from_fields()

    def _sync_port_from_fields(self) -> None:
        name = self.get_field_value("name")
        data_type = self.get_field_value("data_type")

        self.port_in.name = name
        self.port_in.data_type = data_type
        self.port_in.set_color(api.DATA_TYPE_COLORS[data_type])

    def process(self, inputs: dict[str, object]) -> object:
        """
        Return the connected input so the node can be previewed directly.

        This lets double-click preview the output node in the texture viewer
        using the same data path as the subgraph output.
        """
        return inputs.get(self.port_in.name)

    def _on_field_changed(self, node: "GraphOutputNode") -> None:
        self._sync_port_from_fields()

        super()._on_field_changed(node)
