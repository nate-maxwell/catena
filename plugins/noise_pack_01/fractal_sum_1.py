from std_graph_nodes.subgraph import SubgraphNode

from noise_subgraphs import FRACTAL_SUM_1


class FractalSum1Node(SubgraphNode):
    """A node that loads the shipped fractal sum 1 noise subgraph."""

    def __init__(self) -> None:
        super().__init__()
        filepath = str(FRACTAL_SUM_1)
        self._field_values["filepath"] = filepath
        self._cached_filepath = filepath
        self._rebuild_ports()
