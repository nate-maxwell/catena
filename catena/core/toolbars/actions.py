"""
Action functions for the action toolbar buttons.

These are primarily ways to create various nodes or manage the currently
opened file.
"""

import broker

from catena.core import namespace
from catena.core.nodes.create.outro import OutroNode
from catena.core.nodes.create.read import ReadNode
from catena.core.nodes.create.start import StartNode
from catena.core.nodes.create.transition import TransitionNode
from catena.core.nodes.graph import CatenaGraphView
from catena.core.nodes.image.blur import BlurNode
from catena.core.nodes.image.color import ColorNode
from catena.core.nodes.image.contrast import ContrastNode
from catena.core.nodes.image.hsv import HSVNode
from catena.core.nodes.image.levels import LevelsNode
from catena.core.nodes.image.overlay import OverlayNode
from catena.core.nodes.image.sharpen import SharpenNode
from catena.core.nodes.image.threshold import ThresholdNode
from catena.core.nodes.math.add import AddNode
from catena.core.nodes.math.divide import DivideNode
from catena.core.nodes.math.max import MaxNode
from catena.core.nodes.math.min import MinNode
from catena.core.nodes.math.multiply import MultiplyNode
from catena.core.nodes.math.screen import ScreenNode
from catena.core.nodes.math.subtract import SubtractNode
from catena.core.nodes.transform.flip import FlipNode
from catena.core.nodes.transform.offset import OffsetNode
from catena.core.nodes.transform.rotate import RotateNode


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


class CreateActions(object):

    @classmethod
    def action_panel_node(cls, graph_view: CatenaGraphView) -> None:
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
