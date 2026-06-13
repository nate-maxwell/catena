from dataclasses import dataclass


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
    small_grid_color: str = "#2d2d2d"
    large_grid_color: str = "#373737"
    zoom_step: float = 0.12


LAYOUT_DEFAULT = "Default"
LAYOUTS = [LAYOUT_DEFAULT]


@dataclass
class LayoutPreferences(object):
    selected_layout: str = LAYOUT_DEFAULT
