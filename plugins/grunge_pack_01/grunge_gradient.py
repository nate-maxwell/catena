from grunge_subgraphs import GRUNGE_GRADIENT
from std_graph_nodes.subgraph import SubgraphNode


class GrungeGradientNode(SubgraphNode):
    """A node that loads the shipped grunge gradient subgraph."""

    def __init__(self) -> None:
        super().__init__()
        filepath = str(GRUNGE_GRADIENT)
        self._field_values["filepath"] = filepath
        self._cached_filepath = filepath
        self._rebuild_ports()
