from pathlib import Path

_subgraph_path = Path("standard_node_library") / "subgraphs"
"""The directory containing subgraphs shipped with the plugin."""

EDGE_DETECT_GRAPH = _subgraph_path / "edge_detect.cg"
HEIGHT_BLEND = _subgraph_path / "height_blend.cg"
BREAK_OUT = _subgraph_path / "break_out.cg"
