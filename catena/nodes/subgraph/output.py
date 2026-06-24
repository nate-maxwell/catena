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


class GraphOutputProcessor(ProcessorNode):
    """
    A headless processor representing a named output from a subgraph.
    Evaluated by the outer SubgraphNode to retrieve results.
    """

    def __init__(self, name: str = "Output") -> None:
        super().__init__()
        self.name = name

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        """
        Pass the input image through as the subgraph output.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Expects key "Input"
                containing a float32 image.
        Returns:
            numpy.ndarray | None: The subgraph output image.
        """
        return next(iter(inputs.values()), None)


class GraphOutputNode(CatenaNode):
    """
    A node that defines a named output port for a subgraph.
    Appears as an output port on the SubgraphNode in the outer graph.
    """

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        self._processor = GraphOutputProcessor()
        super().__init__(title="Graph Output", width=140, body_height=20)

    def _build(self) -> None:
        self.port_in = self.add_port(PortType.INPUT, "Input", PortDataType.VECTOR4)

        self.add_field(
            FieldDefinition(
                name="name",
                label="Name",
                field_type=FieldType.STR,
                default="Output",
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

    def _on_field_changed(self, node: "GraphOutputNode") -> None:
        name = self.get_field_value("name")
        data_type = self.get_field_value("data_type")

        self.remove_port(self.port_in)
        self.port_in = self.add_port(PortType.INPUT, name, data_type)
        self.port_in.set_color(DATA_TYPE_COLORS[data_type])

        self._processor.name = name
        super()._on_field_changed(node)

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        self._processor.name = self.get_field_value("name")
        name = self.get_field_value("name")
        return self._processor.process({name: inputs.get(name)})
