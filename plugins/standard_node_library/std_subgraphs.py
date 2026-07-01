from pathlib import Path

_subgraph_path = Path(__file__).parent / "subgraphs"
"""The directory containing subgraphs shipped with the plugin."""

EDGE_DETECT_GRAPH = _subgraph_path / "edge_detect.cg"
