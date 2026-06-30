from pathlib import Path

_subgraph_path = Path(__file__).parent / "subgraphs"
"""The directory containing subgraphs shipped with the plugin."""

MOISTURE_NOISE_GRAPH = _subgraph_path / "moisture_noise.cg"
FRACTAL_NOISE_GRAPH = _subgraph_path / "fractal_noise.cg"
