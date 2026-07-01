from std_graph_nodes.subgraph import SubgraphNode

from noise_subgraphs import FRACTAL_SUM_01


class FractalSum01Node(SubgraphNode):
    """A node that loads the shipped fractal sum 01 noise subgraph."""

    def __init__(self) -> None:
        super().__init__()
        filepath = str(FRACTAL_SUM_01)
        self._field_values["filepath"] = filepath
        self._cached_filepath = filepath
        self._rebuild_ports()
