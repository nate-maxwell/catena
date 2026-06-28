from catena import api

from PySide6TK import Resources

from std_modifier_nodes.blur_anisotropic import AnisotropicBlurNode
from std_modifier_nodes.blur import BlurNode
from std_modifier_nodes.blur_radial import RadialBlurNode
from std_modifier_nodes.slope_blur import SlopeBlurNode
from std_modifier_nodes.median_filter import MedianFilterNode
from std_modifier_nodes.sharpen import SharpenNode
from std_modifier_nodes.bevel import BevelNode
from std_modifier_nodes.edge_detect import EdgeDetectNode
from std_modifier_nodes.histogram_scan import HistogramScanNode
from std_modifier_nodes.contrast import ContrastNode
from std_modifier_nodes.hsv import HSVNode
from std_modifier_nodes.invert import InvertNode
from std_modifier_nodes.levels import LevelsNode
from std_modifier_nodes.overlay import OverlayNode
from std_modifier_nodes.normalize import NormalizeNode
from std_modifier_nodes.threshold import ThresholdNode
from std_modifier_nodes.quantize import QuantizeNode


def _add_node(node: type[api.CatenaNode], label: str) -> None:
    api.add_node_to_toolbar("Modifier", node, label, Resources.BUTTON_YELLOW_40X40)


def build_shelf() -> None:
    _add_node(AnisotropicBlurNode, "Aniso\ntropic\nBlur")
    _add_node(BlurNode, "Blur")
    _add_node(RadialBlurNode, "Radial\nBlur")
    _add_node(SlopeBlurNode, "Slope\nBlur")
    _add_node(MedianFilterNode, "Median\nFilter")
    _add_node(SharpenNode, "Sharpen")

    api.add_seperator_to_toolbar("Modifier")

    _add_node(BevelNode, "Bevel")
    _add_node(EdgeDetectNode, "Edge\nDetect")
    _add_node(HistogramScanNode, "Histo\ngram")

    api.add_seperator_to_toolbar("Modifier")

    _add_node(ContrastNode, "Contrst")
    _add_node(HSVNode, "HSV")
    _add_node(InvertNode, "Invert")
    _add_node(LevelsNode, "Levels")
    _add_node(OverlayNode, "Overlay")

    api.add_seperator_to_toolbar("Modifier")

    _add_node(NormalizeNode, "Nrmlize")
    _add_node(ThresholdNode, "Thresh")
    _add_node(QuantizeNode, "Quant")
