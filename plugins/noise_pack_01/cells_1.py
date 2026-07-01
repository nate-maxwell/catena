from std_graph_nodes.subgraph import SubgraphNode

from noise_subgraphs import CELLS_1


class Cells1Node(SubgraphNode):
    """A node that loads the shipped cells 1 noise subgraph."""

    def __init__(self) -> None:
        super().__init__()
        filepath = str(CELLS_1)
        self._field_values["filepath"] = filepath
        self._cached_filepath = filepath
        self._rebuild_ports()
