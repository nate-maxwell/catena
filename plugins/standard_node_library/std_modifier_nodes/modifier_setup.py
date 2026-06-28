import logging

from PySide6TK import Resources

from catena import api
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

logger = logging.getLogger(__name__)

CATEGORY = "Modifier"


def _add_node(node: type[api.CatenaNode], label: str) -> None:
    api.add_node_to_shelf(CATEGORY, node, label, Resources.BUTTON_YELLOW_40X40)


def build_shelf() -> None:
    logger.info("Building std modifier shelf...")

    _add_node(AnisotropicBlurNode, "Aniso\ntropic\nBlur")
    _add_node(BlurNode, "Blur")
    _add_node(RadialBlurNode, "Radial\nBlur")
    _add_node(SlopeBlurNode, "Slope\nBlur")
    _add_node(MedianFilterNode, "Median\nFilter")
    _add_node(SharpenNode, "Sharpen")
    api.add_seperator_to_shelf(CATEGORY)
    _add_node(BevelNode, "Bevel")
    _add_node(EdgeDetectNode, "Edge\nDetect")
    _add_node(HistogramScanNode, "Histo\ngram")
    api.add_seperator_to_shelf(CATEGORY)
    _add_node(ContrastNode, "Contrst")
    _add_node(HSVNode, "HSV")
    _add_node(InvertNode, "Invert")
    _add_node(LevelsNode, "Levels")
    _add_node(OverlayNode, "Overlay")
    api.add_seperator_to_shelf(CATEGORY)
    _add_node(NormalizeNode, "Nrmlize")
    _add_node(ThresholdNode, "Thresh")
    _add_node(QuantizeNode, "Quant")


def build_registry() -> None:
    logger.info("Registering std modifier nodes...")

    api.register_node(CATEGORY, AnisotropicBlurNode)
    api.register_node(CATEGORY, BevelNode)
    api.register_node(CATEGORY, BlurNode)
    api.register_node(CATEGORY, ContrastNode)
    api.register_node(CATEGORY, EdgeDetectNode)
    api.register_node(CATEGORY, HistogramScanNode)
    api.register_node(CATEGORY, HSVNode)
    api.register_node(CATEGORY, InvertNode)
    api.register_node(CATEGORY, LevelsNode)
    api.register_node(CATEGORY, MedianFilterNode)
    api.register_node(CATEGORY, NormalizeNode)
    api.register_node(CATEGORY, OverlayNode)
    api.register_node(CATEGORY, RadialBlurNode)
    api.register_node(CATEGORY, QuantizeNode)
    api.register_node(CATEGORY, SharpenNode)
    api.register_node(CATEGORY, SlopeBlurNode)
    api.register_node(CATEGORY, ThresholdNode)


def initialize() -> None:
    build_shelf()
    build_registry()
