from pathlib import Path

_subgraph_path = Path("noise_pack_01") / "subgraphs"
"""The directory containing subgraphs shipped with the plugin."""

CELLS_1 = _subgraph_path / "cells_1.cg"
CELLS_2 = _subgraph_path / "cells_2.cg"
CELLS_3 = _subgraph_path / "cells_3.cg"

DIRT_1 = _subgraph_path / "dirt_1.cg"
DIRT_2 = _subgraph_path / "dirt_2.cg"

MOISTURE_NOISE_GRAPH = _subgraph_path / "moisture_noise.cg"

FRACTAL_NOISE_GRAPH = _subgraph_path / "fractal_sum_base.cg"
FRACTAL_SUM_1 = _subgraph_path / "fractal_sum_1.cg"
FRACTAL_SUM_2 = _subgraph_path / "fractal_sum_2.cg"
FRACTAL_SUM_3 = _subgraph_path / "fractal_sum_3.cg"
