from std_graph_nodes.subgraph import SubgraphNode

from std_subgraphs import HEIGHT_BLEND


class HeightBlendNode(SubgraphNode):
    """A node that loads the shipped height blend subgraph."""

    def __init__(self) -> None:
        super().__init__()
        filepath = str(HEIGHT_BLEND)
        self._field_values["filepath"] = filepath
        self._cached_filepath = filepath
        self._rebuild_ports()
