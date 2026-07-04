from std_graph_nodes.subgraph import SubgraphNode

from std_subgraphs import EDGE_DETECT


class EdgeDetectNode(SubgraphNode):
    """A node that loads the shipped edge detect subgraph."""

    def __init__(self) -> None:
        super().__init__()
        filepath = str(EDGE_DETECT)
        self._field_values["filepath"] = filepath
        self._cached_filepath = filepath
        self._rebuild_ports()
