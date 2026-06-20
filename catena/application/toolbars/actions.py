"""
Action functions for the action toolbar buttons.

These are primarily ways to file various nodes or manage the currently
opened file.

Actions are kept here instead of with corresponding shelves in case they ever
need to be invoked independent of the shelves.
"""

import broker

from catena.application import namespace
from catena.application.nodes.convert.append import AppendNode
from catena.application.nodes.convert.height_to_ao import HeightToAONode
from catena.application.nodes.convert.height_to_normal import HeightToNormalNode
from catena.application.nodes.convert.split import SplitNode
from catena.application.nodes.file.read import ReadNode
from catena.application.nodes.file.write_albedo import AlbedoNode
from catena.application.nodes.file.write_ambient_occlusion import AONode
from catena.application.nodes.file.write_height import HeightNode
from catena.application.nodes.file.write_metallic import MetallicNode
from catena.application.nodes.file.write_normal import NormalNode
from catena.application.nodes.file.write_roughness import RoughnessNode
from catena.application.nodes.generate.blue_noise import BlueNoiseNode
from catena.application.nodes.generate.bnw_spots import BNWSpotsNode
from catena.application.nodes.generate.cells import CellsNode
from catena.application.nodes.generate.clouds import CloudsNode
from catena.application.nodes.generate.gradient import GradientNode
from catena.application.nodes.generate.perlin_noise import PerlinNoiseNode
from catena.application.nodes.generate.polygon import PolygonNode
from catena.application.nodes.generate.shape import ShapeNode
from catena.application.nodes.generate.voronoi_noise import VoronoiNoiseNode
from catena.application.nodes.generate.white_noise import WhiteNoiseNode
from catena.application.nodes.graph import CatenaGraphView
from catena.application.nodes.image.bevel import BevelNode
from catena.application.nodes.image.blur import BlurNode
from catena.application.nodes.image.color import ColorNode
from catena.application.nodes.image.contrast import ContrastNode
from catena.application.nodes.image.hsv import HSVNode
from catena.application.nodes.image.invert import InvertNode
from catena.application.nodes.image.levels import LevelsNode
from catena.application.nodes.image.normalize import NormalizeNode
from catena.application.nodes.image.overlay import OverlayNode
from catena.application.nodes.image.sharpen import SharpenNode
from catena.application.nodes.image.slope_blur import SlopeBlurNode
from catena.application.nodes.image.threshold import ThresholdNode
from catena.application.nodes.image.warp import WarpNode
from catena.application.nodes.math.add import AddNode
from catena.application.nodes.math.arctan import ArctangentNode
from catena.application.nodes.math.cosin import CosineNode
from catena.application.nodes.math.divide import DivideNode
from catena.application.nodes.math.max import MaxNode
from catena.application.nodes.math.min import MinNode
from catena.application.nodes.math.multiply import MultiplyNode
from catena.application.nodes.math.screen import ScreenNode
from catena.application.nodes.math.sin import SinNode
from catena.application.nodes.math.subtract import SubtractNode
from catena.application.nodes.math.tan import TangentNode
from catena.application.nodes.transform.flip import FlipNode
from catena.application.nodes.transform.offset import OffsetNode
from catena.application.nodes.transform.rotate import RotateNode
from catena.application.nodes.transform.scatter import ScatterNode
from catena.application.nodes.transform.tile import TileNode


class ClientActions(object):

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


class ConvertActions(object):

    @classmethod
    def action_h2m_node(cls, graph_view: CatenaGraphView) -> None:
        coords = graph_view.view_center()
        graph_view.add_node(node=HeightToNormalNode(), x=coords.x(), y=coords.y())

    @classmethod
    def action_h2ao_node(cls, graph_view: CatenaGraphView) -> None:
        coords = graph_view.view_center()
        graph_view.add_node(node=HeightToAONode(), x=coords.x(), y=coords.y())

    @classmethod
    def action_split_node(cls, graph_view: CatenaGraphView) -> None:
        coords = graph_view.view_center()
        graph_view.add_node(node=SplitNode(), x=coords.x(), y=coords.y())

    @classmethod
    def action_append_node(cls, graph_view: CatenaGraphView) -> None:
        coords = graph_view.view_center()
        graph_view.add_node(node=AppendNode(), x=coords.x(), y=coords.y())


class CreateActions(object):

    @classmethod
    def action_read_node(cls, graph_view: CatenaGraphView) -> None:
        coords = graph_view.view_center()
        graph_view.add_node(node=ReadNode(), x=coords.x(), y=coords.y())

    @classmethod
    def action_albedo_node(cls, graph_view: CatenaGraphView) -> None:
        coords = graph_view.view_center()
        graph_view.add_node(node=AlbedoNode(), x=coords.x(), y=coords.y())

    @classmethod
    def action_ao_node(cls, graph_view: CatenaGraphView) -> None:
        coords = graph_view.view_center()
        graph_view.add_node(node=AONode(), x=coords.x(), y=coords.y())

    @classmethod
    def action_height_node(cls, graph_view: CatenaGraphView) -> None:
        coords = graph_view.view_center()
        graph_view.add_node(node=HeightNode(), x=coords.x(), y=coords.y())

    @classmethod
    def action_metallic_node(cls, graph_view: CatenaGraphView) -> None:
        coords = graph_view.view_center()
        graph_view.add_node(node=MetallicNode(), x=coords.x(), y=coords.y())

    @classmethod
    def action_normal_node(cls, graph_view: CatenaGraphView) -> None:
        coords = graph_view.view_center()
        graph_view.add_node(node=NormalNode(), x=coords.x(), y=coords.y())

    @classmethod
    def action_roughness_node(cls, graph_view: CatenaGraphView) -> None:
        coords = graph_view.view_center()
        graph_view.add_node(node=RoughnessNode(), x=coords.x(), y=coords.y())


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
        graph_view.add_node(node=VoronoiNoiseNode(), x=coords.x(), y=coords.y())
