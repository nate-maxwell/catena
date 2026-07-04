from std_graph_nodes.subgraph import SubgraphNode

from noise_subgraphs import DIRT_2


class Dirt2Node(SubgraphNode):
    """A node that loads the shipped dirt 2 noise subgraph."""

    def __init__(self) -> None:
        super().__init__()
        filepath = str(DIRT_2)
        self._field_values["filepath"] = filepath
        self._cached_filepath = filepath
        self._rebuild_ports()
