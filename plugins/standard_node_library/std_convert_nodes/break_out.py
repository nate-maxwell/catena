from std_subgraphs import BREAK_OUT
from std_graph_nodes.subgraph import SubgraphNode


class BreakOutNode(SubgraphNode):
    """A node that loads the shipped break out subgraph."""

    def __init__(self) -> None:
        super().__init__()
        filepath = str(BREAK_OUT)
        self._field_values["filepath"] = filepath
        self._cached_filepath = filepath
        self._rebuild_ports()
