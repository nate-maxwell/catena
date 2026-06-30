from noise_subgraphs import MOISTURE_NOISE_GRAPH
from std_graph_nodes.subgraph import SubgraphNode


class MoistureNoiseNode(SubgraphNode):
    """A node that loads the shipped moisture noise subgraph."""

    def __init__(self) -> None:
        super().__init__()
        filepath = str(MOISTURE_NOISE_GRAPH)
        self._field_values["filepath"] = filepath
        self._cached_filepath = filepath
        self._rebuild_ports()
