from std_graph_nodes.subgraph import SubgraphNode

from noise_subgraphs import DIRT_1


class Dirt1Node(SubgraphNode):
    """A node that loads the shipped dirt 1 noise subgraph."""

    def __init__(self) -> None:
        super().__init__()
        filepath = str(DIRT_1)
        self._field_values["filepath"] = filepath
        self._cached_filepath = filepath
        self._rebuild_ports()
