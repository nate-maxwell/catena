"""
Action functions for the action toolbar buttons.

These are primarily ways to create various nodes or manage the currently
opened file.

Actions are kept here instead of with corresponding shelves in case they ever
need to be invoked independent of the shelves.
"""

import broker

from catena.core import namespace
from catena.core.nodes.convert.height_to_normal import HeightToNormalNode
from catena.core.nodes.create.outro import OutroNode
from catena.core.nodes.create.read import ReadNode
from catena.core.nodes.create.start import StartNode
from catena.core.nodes.create.transition import TransitionNode
from catena.core.nodes.create.write import WriteNode
from catena.core.nodes.generator.blue_noise import BlueNoiseNode
from catena.core.nodes.generator.bnw_spots import BNWSpotsNode
from catena.core.nodes.generator.cells import CellsNode
from catena.core.nodes.generator.clouds import CloudsNode
from catena.core.nodes.generator.crystal_noise import CrystalNoiseNode
from catena.core.nodes.generator.gradient import GradientNode
from catena.core.nodes.generator.perlin_noise import PerlinNoiseNode
from catena.core.nodes.generator.polygon import PolygonNode
from catena.core.nodes.generator.shape import ShapeNode
from catena.core.nodes.generator.white_noise import WhiteNoiseNode
from catena.core.nodes.graph import CatenaGraphView
from catena.core.nodes.image.bevel import BevelNode
from catena.core.nodes.image.blur import BlurNode
from catena.core.nodes.image.color import ColorNode
from catena.core.nodes.image.contrast import ContrastNode
from catena.core.nodes.image.hsv import HSVNode
from catena.core.nodes.image.invert import InvertNode
from catena.core.nodes.image.levels import LevelsNode
from catena.core.nodes.image.normalize import NormalizeNode
from catena.core.nodes.image.overlay import OverlayNode
from catena.core.nodes.image.sharpen import SharpenNode
from catena.core.nodes.image.slope_blur import SlopeBlurNode
from catena.core.nodes.image.threshold import ThresholdNode
from catena.core.nodes.image.warp import WarpNode
from catena.core.nodes.math.add import AddNode
from catena.core.nodes.math.arctan import ArctangentNode
from catena.core.nodes.math.cosin import CosineNode
from catena.core.nodes.math.divide import DivideNode
from catena.core.nodes.math.max import MaxNode
from catena.core.nodes.math.min import MinNode
from catena.core.nodes.math.multiply import MultiplyNode
from catena.core.nodes.math.screen import ScreenNode
from catena.core.nodes.math.sin import SinNode
from catena.core.nodes.math.subtract import SubtractNode
from catena.core.nodes.math.tan import TangentNode
from catena.core.nodes.transform.flip import FlipNode
from catena.core.nodes.transform.offset import OffsetNode
from catena.core.nodes.transform.rotate import RotateNode
from catena.core.nodes.transform.scatter import ScatterNode
from catena.core.nodes.transform.tile import TileNode


class ClientActions(object):

    @classmethod
    def action_save(cls) -> None:
        broker.emit(namespace.CLIENT_SAVE)

    @classmethod
    def action_undo(cls) -> None:
        broker.emit(namespace.CLIENT_UNDO)

    @classmethod
    def action_redo(cls) -> None:
        broker.emit(namespace.CLIENT_REDO)

    @classmethod
    def action_write_files(cls) -> None:
        broker.emit(namespace.NODE_WRITE_FILE)


class CreateActions(object):

    @classmethod
    def action_read_node(cls, graph_view: CatenaGraphView) -> None:
        coords = graph_view.view_center()
        graph_view.add_node(node=ReadNode(), x=coords.x(), y=coords.y())

    @classmethod
    def action_start_node(cls, graph_view: CatenaGraphView) -> None:
        coords = graph_view.view_center()
        graph_view.add_node(node=StartNode(), x=coords.x(), y=coords.y())

    @classmethod
    def action_trans_node(cls, graph_view: CatenaGraphView) -> None:
        coords = graph_view.view_center()
        graph_view.add_node(node=TransitionNode(), x=coords.x(), y=coords.y())

    @classmethod
    def action_outro_node(cls, graph_view: CatenaGraphView) -> None:
        coords = graph_view.view_center()
        graph_view.add_node(node=OutroNode(), x=coords.x(), y=coords.y())

    @classmethod
    def action_write_node(cls, graph_view: CatenaGraphView) -> None:
        coords = graph_view.view_center()
        graph_view.add_node(node=WriteNode(), x=coords.x(), y=coords.y())


class ImageActions(object):

    @classmethod
    def action_overlay_node(cls, graph_view: CatenaGraphView) -> None:
        coords = graph_view.view_center()
        graph_view.add_node(node=OverlayNode(), x=coords.x(), y=coords.y())

    @classmethod
    def action_blur_node(cls, graph_view: CatenaGraphView) -> None:
        coords = graph_view.view_center()
        graph_view.add_node(node=BlurNode(), x=coords.x(), y=coords.y())

    @classmethod
    def action_hsv_node(cls, graph_view: CatenaGraphView) -> None:
        coords = graph_view.view_center()
        graph_view.add_node(node=HSVNode(), x=coords.x(), y=coords.y())

    @classmethod
    def action_levels_node(cls, graph_view: CatenaGraphView) -> None:
        coords = graph_view.view_center()
        graph_view.add_node(node=LevelsNode(), x=coords.x(), y=coords.y())

    @classmethod
    def action_sharpen_node(cls, graph_view: CatenaGraphView) -> None:
        coords = graph_view.view_center()
        graph_view.add_node(node=SharpenNode(), x=coords.x(), y=coords.y())

    @classmethod
    def action_contrast_node(cls, graph_view: CatenaGraphView) -> None:
        coords = graph_view.view_center()
        graph_view.add_node(node=ContrastNode(), x=coords.x(), y=coords.y())

    @classmethod
    def action_threshold_node(cls, graph_view: CatenaGraphView) -> None:
        coords = graph_view.view_center()
        graph_view.add_node(node=ThresholdNode(), x=coords.x(), y=coords.y())

    @classmethod
    def action_color_node(cls, graph_view: CatenaGraphView) -> None:
        coords = graph_view.view_center()
        graph_view.add_node(node=ColorNode(), x=coords.x(), y=coords.y())

    @classmethod
    def action_invert_node(cls, graph_view: CatenaGraphView) -> None:
        coords = graph_view.view_center()
        graph_view.add_node(node=InvertNode(), x=coords.x(), y=coords.y())

    @classmethod
    def action_warp_node(cls, graph_view: CatenaGraphView) -> None:
        coords = graph_view.view_center()
        graph_view.add_node(node=WarpNode(), x=coords.x(), y=coords.y())

    @classmethod
    def action_bevel_node(cls, graph_view: CatenaGraphView) -> None:
        coords = graph_view.view_center()
        graph_view.add_node(node=BevelNode(), x=coords.x(), y=coords.y())

    @classmethod
    def action_slope_blur_node(cls, graph_view: CatenaGraphView) -> None:
        coords = graph_view.view_center()
        graph_view.add_node(node=SlopeBlurNode(), x=coords.x(), y=coords.y())

    @classmethod
    def action_normalize_node(cls, graph_view: CatenaGraphView) -> None:
        coords = graph_view.view_center()
        graph_view.add_node(node=NormalizeNode(), x=coords.x(), y=coords.y())


class XformActions(object):

    @classmethod
    def action_flip_node(cls, graph_view: CatenaGraphView) -> None:
        coords = graph_view.view_center()
        graph_view.add_node(node=FlipNode(), x=coords.x(), y=coords.y())

    @classmethod
    def action_rotate_node(cls, graph_view: CatenaGraphView) -> None:
        coords = graph_view.view_center()
        graph_view.add_node(node=RotateNode(), x=coords.x(), y=coords.y())

    @classmethod
    def action_offset_node(cls, graph_view: CatenaGraphView) -> None:
        coords = graph_view.view_center()
        graph_view.add_node(node=OffsetNode(), x=coords.x(), y=coords.y())

    @classmethod
    def action_tile_node(cls, graph_view: CatenaGraphView) -> None:
        coords = graph_view.view_center()
        graph_view.add_node(node=TileNode(), x=coords.x(), y=coords.y())

    @classmethod
    def action_scatter_node(cls, graph_view: CatenaGraphView) -> None:
        coords = graph_view.view_center()
        graph_view.add_node(node=ScatterNode(), x=coords.x(), y=coords.y())


class MathActions(object):

    @classmethod
    def action_add_node(cls, graph_view: CatenaGraphView) -> None:
        coords = graph_view.view_center()
        graph_view.add_node(node=AddNode(), x=coords.x(), y=coords.y())

    @classmethod
    def action_multiply_node(cls, graph_view: CatenaGraphView) -> None:
        coords = graph_view.view_center()
        graph_view.add_node(node=MultiplyNode(), x=coords.x(), y=coords.y())

    @classmethod
    def action_subtract_node(cls, graph_view: CatenaGraphView) -> None:
        coords = graph_view.view_center()
        graph_view.add_node(node=SubtractNode(), x=coords.x(), y=coords.y())

    @classmethod
    def action_divide_node(cls, graph_view: CatenaGraphView) -> None:
        coords = graph_view.view_center()
        graph_view.add_node(node=DivideNode(), x=coords.x(), y=coords.y())

    @classmethod
    def action_min_node(cls, graph_view: CatenaGraphView) -> None:
        coords = graph_view.view_center()
        graph_view.add_node(node=MinNode(), x=coords.x(), y=coords.y())

    @classmethod
    def action_max_node(cls, graph_view: CatenaGraphView) -> None:
        coords = graph_view.view_center()
        graph_view.add_node(node=MaxNode(), x=coords.x(), y=coords.y())

    @classmethod
    def action_screen_node(cls, graph_view: CatenaGraphView) -> None:
        coords = graph_view.view_center()
        graph_view.add_node(node=ScreenNode(), x=coords.x(), y=coords.y())

    @classmethod
    def action_sin_node(cls, graph_view: CatenaGraphView) -> None:
        coords = graph_view.view_center()
        graph_view.add_node(node=SinNode(), x=coords.x(), y=coords.y())

    @classmethod
    def action_cosin_node(cls, graph_view: CatenaGraphView) -> None:
        coords = graph_view.view_center()
        graph_view.add_node(node=CosineNode(), x=coords.x(), y=coords.y())

    @classmethod
    def action_tan_node(cls, graph_view: CatenaGraphView) -> None:
        coords = graph_view.view_center()
        graph_view.add_node(node=TangentNode(), x=coords.x(), y=coords.y())

    @classmethod
    def action_arctan_node(cls, graph_view: CatenaGraphView) -> None:
        coords = graph_view.view_center()
        graph_view.add_node(node=ArctangentNode(), x=coords.x(), y=coords.y())


class GeneratorActions(object):

    @classmethod
    def action_perlin_noise_node(cls, graph_view: CatenaGraphView) -> None:
        coords = graph_view.view_center()
        graph_view.add_node(node=PerlinNoiseNode(), x=coords.x(), y=coords.y())

    @classmethod
    def action_blue_noise_node(cls, graph_view: CatenaGraphView) -> None:
        coords = graph_view.view_center()
        graph_view.add_node(node=BlueNoiseNode(), x=coords.x(), y=coords.y())

    @classmethod
    def action_bnw_spots_node(cls, graph_view: CatenaGraphView) -> None:
        coords = graph_view.view_center()
        graph_view.add_node(node=BNWSpotsNode(), x=coords.x(), y=coords.y())

    @classmethod
    def action_cells_node(cls, graph_view: CatenaGraphView) -> None:
        coords = graph_view.view_center()
        graph_view.add_node(node=CellsNode(), x=coords.x(), y=coords.y())

    @classmethod
    def action_clouds_node(cls, graph_view: CatenaGraphView) -> None:
        coords = graph_view.view_center()
        graph_view.add_node(node=CloudsNode(), x=coords.x(), y=coords.y())

    @classmethod
    def action_gradient_node(cls, graph_view: CatenaGraphView) -> None:
        coords = graph_view.view_center()
        graph_view.add_node(node=GradientNode(), x=coords.x(), y=coords.y())

    @classmethod
    def action_white_noise_node(cls, graph_view: CatenaGraphView) -> None:
        coords = graph_view.view_center()
        graph_view.add_node(node=WhiteNoiseNode(), x=coords.x(), y=coords.y())

    @classmethod
    def action_shape_node(cls, graph_view: CatenaGraphView) -> None:
        coords = graph_view.view_center()
        graph_view.add_node(node=ShapeNode(), x=coords.x(), y=coords.y())

    @classmethod
    def action_polygon_node(cls, graph_view: CatenaGraphView) -> None:
        coords = graph_view.view_center()
        graph_view.add_node(node=PolygonNode(), x=coords.x(), y=coords.y())

    @classmethod
    def action_crystal_noise_node(cls, graph_view: CatenaGraphView) -> None:
        coords = graph_view.view_center()
        graph_view.add_node(node=CrystalNoiseNode(), x=coords.x(), y=coords.y())


class ConvertActions(object):

    @classmethod
    def action_h2m_node(cls, graph_view: CatenaGraphView) -> None:
        coords = graph_view.view_center()
        graph_view.add_node(node=HeightToNormalNode(), x=coords.x(), y=coords.y())
