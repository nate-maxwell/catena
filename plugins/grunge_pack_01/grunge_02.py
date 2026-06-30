from grunge_subgraphs import GRUNGE_02_GRAPH
from std_graph_nodes.subgraph import SubgraphNode


class Grunge02Node(SubgraphNode):
    """A node that loads the shipped grunge02 subgraph."""

    def __init__(self) -> None:
        super().__init__()
        filepath = str(GRUNGE_02_GRAPH)
        self._field_values["filepath"] = filepath
        self._cached_filepath = filepath
        self._rebuild_ports()
