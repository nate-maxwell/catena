from typing import Optional

import numpy
from PySide6TK.Nodes import FieldDefinition
from PySide6TK.Nodes import FieldType
from PySide6TK.Nodes import PortType

from catena.nodes.node_gui import CatenaNode
from catena.nodes.node_processor import ProcessorNode
from catena.nodes.subgraph import IMAGE_NODE_COLOR
from catena.nodes.data import DATA_TYPE_COLORS
from catena.nodes.data import PortDataType

_PORT_TYPES = [v for k, v in vars(PortDataType).items() if not k.startswith("_")]


class GraphInputProcessor(ProcessorNode):
    """
    A headless processor representing a named input to a subgraph.
    The injected value is set directly on this processor before evaluation.
    """

    def __init__(self, name: str = "Input") -> None:
        super().__init__()
        self.name = name
        self._injected: Optional[numpy.ndarray] = None

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


class GraphInputNode(CatenaNode):
    """
    A node that defines a named input port for a subgraph.
    Appears as an input port on the SubgraphNode in the outer graph.
    """

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        self._processor = GraphInputProcessor()
        super().__init__(title="Graph Input", width=140, body_height=20)

    def _build(self) -> None:
        self.port_out = self.add_port(PortType.OUTPUT, "Output", PortDataType.VECTOR4)

        self.add_field(
            FieldDefinition(
                name="name",
                label="Name",
                field_type=FieldType.STR,
                default="Input",
            )
        )
        self.add_field(
            FieldDefinition(
                name="data_type",
                label="Type",
                field_type=FieldType.CHOICE,
                default=PortDataType.VECTOR4,
                options=_PORT_TYPES,
            )
        )

    def _on_field_changed(self, node: "GraphInputNode") -> None:
        name = self.get_field_value("name")
        data_type = self.get_field_value("data_type")

        self.remove_port(self.port_out)
        self.port_out = self.add_port(PortType.OUTPUT, name, data_type)
        self.port_out.set_color(DATA_TYPE_COLORS[data_type])

        self._processor.name = name
        super()._on_field_changed(node)

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        self._processor.name = self.get_field_value("name")
        return self._processor.process(inputs)
