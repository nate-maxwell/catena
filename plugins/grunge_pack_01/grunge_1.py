from grunge_subgraphs import GRUNGE_1
from std_graph_nodes.subgraph import SubgraphNode


class Grunge1Node(SubgraphNode):
    """A node that loads the shipped grunge1 subgraph."""

    def __init__(self) -> None:
        super().__init__()
        filepath = str(GRUNGE_1)
        self._field_values["filepath"] = filepath
        self._cached_filepath = filepath
        self._rebuild_ports()
