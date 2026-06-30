from noise_subgraphs import FRACTAL_NOISE_GRAPH
from std_graph_nodes.subgraph import SubgraphNode


class FractalSumBaseNode(SubgraphNode):
    """A node that loads the shipped fractal sum base noise subgraph."""

    def __init__(self) -> None:
        super().__init__()
        filepath = str(FRACTAL_NOISE_GRAPH)
        self._field_values["filepath"] = filepath
        self._cached_filepath = filepath
        self._rebuild_ports()
