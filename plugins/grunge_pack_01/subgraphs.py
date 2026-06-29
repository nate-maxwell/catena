from pathlib import Path

_subgraph_path = Path(__file__).parent / "subgraphs"
"""The directory containing subgraphs shipped with the plugin."""

MOISTURE_NOISE_GRAPH = _subgraph_path / "moisture_noise.cg"
GRUNGE_01_GRAPH = _subgraph_path / "grunge_01.cg"
