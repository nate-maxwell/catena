"""
Action functions for the action toolbar buttons.

These are primarily ways to file various nodes or manage the currently
opened file.

Actions are kept here instead of with corresponding shelves in case they ever
need to be invoked independent of the shelves.
"""

import broker

from catena import namespace
from catena.nodes.convert.append import AppendNode
from catena.nodes.convert.float_to_int import FloatToIntNode
from catena.nodes.convert.float_to_vec4 import FloatToVec4Node
from catena.nodes.convert.height_to_ao import HeightToAONode
from catena.nodes.convert.height_to_normal import HeightToNormalNode
from catena.nodes.convert.int_to_float import IntToFloatNode
from catena.nodes.convert.int_to_vec4 import IntToVec4Node
from catena.nodes.convert.split import SplitNode
from catena.nodes.file.read import ReadNode
from catena.nodes.file.write import WriteNode
from catena.nodes.flood_fill.ff_to_gradient import FloodFillToGradientNode
from catena.nodes.flood_fill.ff_to_greyscale import FloodFillToGreyscaleNode
from catena.nodes.flood_fill.ff_to_rand_color import FloodFillToRandomColorNode
from catena.nodes.flood_fill.flood_fill import FloodFillNode
from catena.nodes.generate.blue_noise import BlueNoiseNode
from catena.nodes.generate.bnw_spots import BNWSpotsNode
from catena.nodes.generate.cells import CellsNode
from catena.nodes.generate.checker import CheckerNode
from catena.nodes.generate.clouds import CloudsNode
from catena.nodes.generate.color import ColorNode
from catena.nodes.generate.fibers import FibersNode
from catena.nodes.generate.float import FloatNode
from catena.nodes.generate.gradient import GradientNode
from catena.nodes.generate.grunge import GrungeNode
from catena.nodes.generate.mold import MoldNode
from catena.nodes.generate.perlin_noise import PerlinNoiseNode
from catena.nodes.generate.pink_noise import PinkNoiseNode
from catena.nodes.generate.polygon import PolygonNode
from catena.nodes.generate.scratches import ScratchesNode
from catena.nodes.generate.shape import ShapeNode
from catena.nodes.generate.voronoi_noise import VoronoiNoiseNode
from catena.nodes.generate.weave import WeaveNode
from catena.nodes.generate.white_noise import WhiteNoiseNode
from catena.nodes.math.add import AddNode
from catena.nodes.math.arctan import ArctangentNode
from catena.nodes.math.ceil import CeilNode
from catena.nodes.math.cosine import CosineNode
from catena.nodes.math.divide import DivideNode
from catena.nodes.math.floor import FloorNode
from catena.nodes.math.max import MaxNode
from catena.nodes.math.min import MinNode
from catena.nodes.math.multiply import MultiplyNode
from catena.nodes.math.screen import ScreenNode
from catena.nodes.math.sin import SinNode
from catena.nodes.math.subtract import SubtractNode
from catena.nodes.math.tan import TangentNode
from catena.nodes.modifier.bevel import BevelNode
from catena.nodes.modifier.blur import BlurNode
from catena.nodes.modifier.blur_anisotropic import AnisotropicBlurNode
from catena.nodes.modifier.blur_radial import RadialBlurNode
from catena.nodes.modifier.contrast import ContrastNode
from catena.nodes.modifier.edge_detect import EdgeDetectNode
from catena.nodes.modifier.histogram_scan import HistogramScanNode
from catena.nodes.modifier.hsv import HSVNode
from catena.nodes.modifier.invert import InvertNode
from catena.nodes.modifier.levels import LevelsNode
from catena.nodes.modifier.median_filter import MedianFilterNode
from catena.nodes.modifier.normalize import NormalizeNode
from catena.nodes.modifier.overlay import OverlayNode
from catena.nodes.modifier.quantize import QuantizeNode
from catena.nodes.modifier.sharpen import SharpenNode
from catena.nodes.modifier.slope_blur import SlopeBlurNode
from catena.nodes.modifier.threshold import ThresholdNode
from catena.nodes.subgraph.input import GraphInputNode
from catena.nodes.subgraph.output import GraphOutputNode
from catena.nodes.subgraph.subgraph import SubgraphNode
from catena.nodes.transform.flip import FlipNode
from catena.nodes.transform.offset import OffsetNode
from catena.nodes.transform.rotate_scale import RotateScaleNode
from catena.nodes.transform.scatter import ScatterNode
from catena.nodes.transform.tile import TileNode
from catena.nodes.transform.warp import WarpNode
from catena.nodes.transform.warp_directional import DirectionalWarpNode
from catena.nodes.transform.warp_vector import VectorWarpNode
from catena.panes.node_graph.node_graph import NodeGraphPane

_graph_pane: NodeGraphPane | None = None


def init_graph_pane(graph_pane: NodeGraphPane | None = None) -> None:
    global _graph_pane
    if graph_pane is None:
        return

    _graph_pane = graph_pane


def add_to_focussed(node) -> None:
    if graph_view := _graph_pane.get_focused_graph():
        graph_view.add_node_to_center(node())


class GraphActions(object):

    @classmethod
    def action_save(cls) -> None:
        broker.emit(namespace.FILE_SAVE)

    @classmethod
    def action_undo(cls) -> None:
        broker.emit(namespace.FILE_UNDO)

    @classmethod
    def action_redo(cls) -> None:
        broker.emit(namespace.FILE_REDO)

    @classmethod
    def action_write_files(cls) -> None:
        broker.emit(namespace.NODE_WRITE_FILE)

    @classmethod
    def action_read_node(cls) -> None:
        add_to_focussed(ReadNode)

    @classmethod
    def action_write_node(cls) -> None:
        add_to_focussed(WriteNode)


class SubgraphActions(object):

    @classmethod
    def action_graph_input_node(cls) -> None:
        add_to_focussed(GraphInputNode)

    @classmethod
    def action_graph_output_node(cls) -> None:
        add_to_focussed(GraphOutputNode)

    @classmethod
    def action_sub_graph_node(cls) -> None:
        add_to_focussed(SubgraphNode)


class ConvertActions(object):

    @classmethod
    def action_h2m_node(cls) -> None:
        add_to_focussed(HeightToNormalNode)

    @classmethod
    def action_h2ao_node(cls) -> None:
        add_to_focussed(HeightToAONode)

    @classmethod
    def action_split_node(cls) -> None:
        add_to_focussed(SplitNode)

    @classmethod
    def action_append_node(cls) -> None:
        add_to_focussed(AppendNode)

    @classmethod
    def action_int_to_float_node(cls) -> None:
        add_to_focussed(IntToFloatNode)

    @classmethod
    def action_int_to_vec4_node(cls) -> None:
        add_to_focussed(IntToVec4Node)

    @classmethod
    def action_float_to_int_node(cls) -> None:
        add_to_focussed(FloatToIntNode)

    @classmethod
    def action_float_to_vec4_node(cls) -> None:
        add_to_focussed(FloatToVec4Node)


class ModifierActions(object):

    @classmethod
    def action_overlay_node(cls) -> None:
        add_to_focussed(OverlayNode)

    @classmethod
    def action_blur_node(cls) -> None:
        add_to_focussed(BlurNode)

    @classmethod
    def action_hsv_node(cls) -> None:
        add_to_focussed(HSVNode)

    @classmethod
    def action_levels_node(cls) -> None:
        add_to_focussed(LevelsNode)

    @classmethod
    def action_sharpen_node(cls) -> None:
        add_to_focussed(SharpenNode)

    @classmethod
    def action_contrast_node(cls) -> None:
        add_to_focussed(ContrastNode)

    @classmethod
    def action_threshold_node(cls) -> None:
        add_to_focussed(ThresholdNode)

    @classmethod
    def action_historgram_node(cls) -> None:
        add_to_focussed(HistogramScanNode)

    @classmethod
    def action_edge_detect_node(cls) -> None:
        add_to_focussed(EdgeDetectNode)

    @classmethod
    def action_invert_node(cls) -> None:
        add_to_focussed(InvertNode)

    @classmethod
    def action_bevel_node(cls) -> None:
        add_to_focussed(BevelNode)

    @classmethod
    def action_slope_blur_node(cls) -> None:
        add_to_focussed(SlopeBlurNode)

    @classmethod
    def action_normalize_node(cls) -> None:
        add_to_focussed(NormalizeNode)

    @classmethod
    def action_blur_anisotropic_node(cls) -> None:
        add_to_focussed(AnisotropicBlurNode)

    @classmethod
    def action_blur_radial_node(cls) -> None:
        add_to_focussed(RadialBlurNode)

    @classmethod
    def action_median_filter_node(cls) -> None:
        add_to_focussed(MedianFilterNode)

    @classmethod
    def action_quantize_node(cls) -> None:
        add_to_focussed(QuantizeNode)


class XformActions(object):

    @classmethod
    def action_flip_node(cls) -> None:
        add_to_focussed(FlipNode)

    @classmethod
    def action_rotate_node(cls) -> None:
        add_to_focussed(RotateScaleNode)

    @classmethod
    def action_offset_node(cls) -> None:
        add_to_focussed(OffsetNode)

    @classmethod
    def action_tile_node(cls) -> None:
        add_to_focussed(TileNode)

    @classmethod
    def action_scatter_node(cls) -> None:
        add_to_focussed(ScatterNode)

    @classmethod
    def action_warp_node(cls) -> None:
        add_to_focussed(WarpNode)

    @classmethod
    def action_directional_warp_node(cls) -> None:
        add_to_focussed(DirectionalWarpNode)

    @classmethod
    def action_vector_warp_node(cls) -> None:
        add_to_focussed(VectorWarpNode)


class MathActions(object):

    @classmethod
    def action_add_node(cls) -> None:
        add_to_focussed(AddNode)

    @classmethod
    def action_multiply_node(cls) -> None:
        add_to_focussed(MultiplyNode)

    @classmethod
    def action_subtract_node(cls) -> None:
        add_to_focussed(SubtractNode)

    @classmethod
    def action_divide_node(cls) -> None:
        add_to_focussed(DivideNode)

    @classmethod
    def action_min_node(cls) -> None:
        add_to_focussed(MinNode)

    @classmethod
    def action_ceil_node(cls) -> None:
        add_to_focussed(CeilNode)

    @classmethod
    def action_floor_node(cls) -> None:
        add_to_focussed(FloorNode)

    @classmethod
    def action_max_node(cls) -> None:
        add_to_focussed(MaxNode)

    @classmethod
    def action_screen_node(cls) -> None:
        add_to_focussed(ScreenNode)

    @classmethod
    def action_sin_node(cls) -> None:
        add_to_focussed(SinNode)

    @classmethod
    def action_cosine_node(cls) -> None:
        add_to_focussed(CosineNode)

    @classmethod
    def action_tan_node(cls) -> None:
        add_to_focussed(TangentNode)

    @classmethod
    def action_arctan_node(cls) -> None:
        add_to_focussed(ArctangentNode)


class GeneratorActions(object):

    @classmethod
    def action_perlin_noise_node(cls) -> None:
        add_to_focussed(PerlinNoiseNode)

    @classmethod
    def action_blue_noise_node(cls) -> None:
        add_to_focussed(BlueNoiseNode)

    @classmethod
    def action_bnw_spots_node(cls) -> None:
        add_to_focussed(BNWSpotsNode)

    @classmethod
    def action_checker_node(cls) -> None:
        add_to_focussed(CheckerNode)

    @classmethod
    def action_weave_node(cls) -> None:
        add_to_focussed(WeaveNode)

    @classmethod
    def action_fibers_node(cls) -> None:
        add_to_focussed(FibersNode)

    @classmethod
    def action_cells_node(cls) -> None:
        add_to_focussed(CellsNode)

    @classmethod
    def action_clouds_node(cls) -> None:
        add_to_focussed(CloudsNode)

    @classmethod
    def action_gradient_node(cls) -> None:
        add_to_focussed(GradientNode)

    @classmethod
    def action_white_noise_node(cls) -> None:
        add_to_focussed(WhiteNoiseNode)

    @classmethod
    def action_shape_node(cls) -> None:
        add_to_focussed(ShapeNode)

    @classmethod
    def action_polygon_node(cls) -> None:
        add_to_focussed(PolygonNode)

    @classmethod
    def action_voronoi_noise_node(cls) -> None:
        add_to_focussed(VoronoiNoiseNode)

    @classmethod
    def action_grunge_one_node(cls) -> None:
        add_to_focussed(GrungeNode)

    @classmethod
    def action_color_node(cls) -> None:
        add_to_focussed(ColorNode)

    @classmethod
    def action_scratches_node(cls) -> None:
        add_to_focussed(ScratchesNode)

    @classmethod
    def action_mold_node(cls) -> None:
        add_to_focussed(MoldNode)

    @classmethod
    def action_pink_noise_node(cls) -> None:
        add_to_focussed(PinkNoiseNode)

    @classmethod
    def action_float_node(cls) -> None:
        add_to_focussed(FloatNode)


class FloodFillActions(object):

    @classmethod
    def action_flood_fill_node(cls) -> None:
        add_to_focussed(FloodFillNode)

    @classmethod
    def action_ff_to_greyscale_node(cls) -> None:
        add_to_focussed(FloodFillToGreyscaleNode)

    @classmethod
    def action_ff_to_gradient_node(cls) -> None:
        add_to_focussed(FloodFillToGradientNode)

    @classmethod
    def action_ff_to_rand_color_node(cls) -> None:
        add_to_focussed(FloodFillToRandomColorNode)
