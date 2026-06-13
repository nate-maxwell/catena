"""
Action functions for the action toolbar buttons.

These are primarily ways to create various nodes or manage the currently
opened file.
"""

from catena.core.nodes.create.outro import OutroNode

# create nodes
from catena.core.nodes.create.read import ReadNode
from catena.core.nodes.create.start import StartNode
from catena.core.nodes.create.transition import TransitionNode

# graph
from catena.core.nodes.graph import CatenaGraphView

# image nodes
from catena.core.nodes.image.overlay import OverlayNode
from catena.core.nodes.image.blur import BlurNode
from catena.core.nodes.image.contrast import ContrastNode
from catena.core.nodes.image.hsv import HSVNode
from catena.core.nodes.image.levels import LevelsNode
from catena.core.nodes.image.multiply import MultiplyNode
from catena.core.nodes.image.sharpen import SharpenNode
from catena.core.nodes.image.threshold import ThresholdNode

# transform nodes
from catena.core.nodes.transform.flip import FlipNode
from catena.core.nodes.transform.offset import OffsetNode
from catena.core.nodes.transform.rotate import RotateNode


class ClientActions(object):

    @classmethod
    def action_save(cls) -> None: ...

    @classmethod
    def action_undo(cls) -> None: ...

    @classmethod
    def action_redo(cls) -> None: ...


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
    def action_blend_node(cls, graph_view: CatenaGraphView) -> None:
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
    def action_multiply_node(cls, graph_view: CatenaGraphView) -> None:
        coords = graph_view.view_center()
        graph_view.add_node(node=MultiplyNode(), x=coords.x(), y=coords.y())

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
