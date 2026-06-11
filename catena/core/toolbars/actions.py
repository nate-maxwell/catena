"""
Action functions for the action toolbar buttons.

These are primarily ways to create various nodes or manage the currently
opened file.
"""

from catena.core.nodes.graph import CatenaGraphView
from catena.core.nodes.panel import PanelNode
from catena.core.nodes.start import StartNode
from catena.core.nodes.transition import TransitionNode
from catena.core.nodes.outro import OutroNode


def action_save() -> None: ...


def action_undo() -> None: ...


def action_reado() -> None: ...


def action_panel_node(graph_view: CatenaGraphView) -> None:
    coords = graph_view.view_center()
    graph_view.add_node(node=PanelNode(), x=coords.x(), y=coords.y())


def action_start_node(graph_view: CatenaGraphView) -> None:
    coords = graph_view.view_center()
    graph_view.add_node(node=StartNode(), x=coords.x(), y=coords.y())


def action_trans_node(graph_view: CatenaGraphView) -> None:
    coords = graph_view.view_center()
    graph_view.add_node(node=TransitionNode(), x=coords.x(), y=coords.y())


def action_outro_node(graph_view: CatenaGraphView) -> None:
    coords = graph_view.view_center()
    graph_view.add_node(node=OutroNode(), x=coords.x(), y=coords.y())


def action_overlay_node(graph_view: CatenaGraphView) -> None: ...


def action_color_grade_node(graph_view: CatenaGraphView) -> None: ...


def action_crop_node(graph_view: CatenaGraphView) -> None: ...


def action_zoom_node(graph_view: CatenaGraphView) -> None: ...


def action_water_mark_node(graph_view: CatenaGraphView) -> None: ...
