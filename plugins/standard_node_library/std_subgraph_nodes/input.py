from typing import Optional

import numpy

from catena import api
from std_subgraph_nodes import IMAGE_NODE_COLOR

_PORT_TYPES = [v for k, v in vars(api.PortDataType).items() if not k.startswith("_")]


class GraphInputNode(api.CatenaNode):
    """
    A node that defines a named input port for a subgraph.
    Appears as an input port on the SubgraphNode in the outer graph.
    """

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        super().__init__(title="Graph Input", width=140, body_height=20)

    def _build(self) -> None:
        self.port_out = self.add_port(
            api.PortType.OUTPUT, "Output", api.PortDataType.VECTOR4
        )

        self.add_field(
            api.FieldDefinition(
                name="name",
                label="Name",
                field_type=api.FieldType.STR,
                default="Input",
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

    def _on_field_changed(self, node: "GraphInputNode") -> None:
        name = self.get_field_value("name")
        data_type = self.get_field_value("data_type")

        self.remove_port(self.port_out)
        self.port_out = self.add_port(api.PortType.OUTPUT, name, data_type)
        self.port_out.set_color(api.DATA_TYPE_COLORS[data_type])

        super()._on_field_changed(node)

    def inject(self, value: Optional[numpy.ndarray]) -> None:
        """
        Inject an input value from the outer graph into this subgraph input.

        Args:
            value (numpy.ndarray | None): The image to inject.
        """
        self._injected = value

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        """
        Return the injected value from the outer graph.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Unused.
        Returns:
            numpy.ndarray | None: The injected image.
        """
        return self._injected
