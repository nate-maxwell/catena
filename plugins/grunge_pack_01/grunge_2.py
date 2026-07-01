from grunge_subgraphs import GRUNGE_2
from std_graph_nodes.subgraph import SubgraphNode


class Grunge2Node(SubgraphNode):
    """A node that loads the shipped grunge2 subgraph."""

    def __init__(self) -> None:
        super().__init__()
        filepath = str(GRUNGE_2)
        self._field_values["filepath"] = filepath
        self._cached_filepath = filepath
        self._rebuild_ports()
