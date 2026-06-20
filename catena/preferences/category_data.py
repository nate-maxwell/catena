from dataclasses import dataclass

from PySide6TK import QtGui


@dataclass
class GeneralPreferences(object):
    auto_save_interval: int = 0


WIRE_STYLE_BEZIER = "Bezier"
WIRE_STYLE_STRAIGHT = "Straight"
WIRE_STYLES = [
    WIRE_STYLE_BEZIER,
    WIRE_STYLE_STRAIGHT,
]


@dataclass
class NodeGraphPreferences(object):
    wire_style: str = WIRE_STYLE_BEZIER
    grid_size_small: int = 20
    grid_size_large: int = 100
    color_grid_bg: str = QtGui.QColor(30, 30, 30).name()
    color_grid_small: str = QtGui.QColor(45, 45, 45).name()
    color_grid_large: str = QtGui.QColor(55, 55, 55).name()
    zoom_step: float = 0.12
    zoom_min: float = 0.1
    zoom_max: float = 4.0


LAYOUT_DEFAULT = "Default"
LAYOUTS = [LAYOUT_DEFAULT]


@dataclass
class LayoutPreferences(object):
    selected_layout: str = LAYOUT_DEFAULT
