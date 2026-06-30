from pathlib import Path

_subgraph_path = Path(__file__).parent / "subgraphs"
"""The directory containing subgraphs shipped with the plugin."""

MOISTURE_NOISE_GRAPH = _subgraph_path / "moisture_noise.cg"

FRACTAL_NOISE_GRAPH = _subgraph_path / "fractal_sum_base.cg"
FRACTAL_SUM_01 = _subgraph_path / "fractal_sum_01.cg"
FRACTAL_SUM_02 = _subgraph_path / "fractal_sum_02.cg"
FRACTAL_SUM_03 = _subgraph_path / "fractal_sum_03.cg"
