from __future__ import annotations

import logging
from functools import wraps

from PySide6 import QtWidgets

from catena.nodes.graph import GuiGraphView
from catena.panes.node_graph.node_graph import NodeGraphPane

from mimimap import MinimapWidget

logger = logging.getLogger(__name__)

_MINIMAP_ATTR = "_catena_minimap_widget"
_PATCH_FLAG = "_catena_minimap_patch_applied"


def _attach_minimap(graph_view: GuiGraphView) -> None:
    if getattr(graph_view, _MINIMAP_ATTR, None) is not None:
        return

    minimap = MinimapWidget(graph_view, graph_view)
    minimap.show()
    minimap.raise_()
    setattr(graph_view, _MINIMAP_ATTR, minimap)
    logger.info("Attached minimap to graph view %s", graph_view)


def _patch_node_graph_pane() -> None:
    if getattr(NodeGraphPane, _PATCH_FLAG, False):
        return

    original_open_new_tab = NodeGraphPane._open_new_tab

    @wraps(original_open_new_tab)
    def _open_new_tab_with_minimap(self: NodeGraphPane, file_path):
        view = original_open_new_tab(self, file_path)
        if isinstance(view, GuiGraphView):
            _attach_minimap(view)
        return view

    NodeGraphPane._open_new_tab = _open_new_tab_with_minimap
    setattr(NodeGraphPane, _PATCH_FLAG, True)


def _attach_existing_views() -> None:
    app = QtWidgets.QApplication.instance()
    if app is None:
        return

    for window in app.topLevelWidgets():
        pane = getattr(window, "pane_node_graph", None)
        if not isinstance(pane, NodeGraphPane):
            continue

        for index in range(pane.tab_widget.count()):
            view = pane.tab_widget.widget(index)
            if isinstance(view, GuiGraphView):
                _attach_minimap(view)


def _install_minimaps() -> None:
    _patch_node_graph_pane()
    _attach_existing_views()


_install_minimaps()
