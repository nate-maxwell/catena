"""
# Viewport Widget

The primary housing widget for all components that make up the primary content
widget of the viewport pane.
"""

from PySide6TK import QtWidgets

from catena.core.panes.viewport import timeline
from catena.core.panes.viewport import image_view


class ViewportWidget(QtWidgets.QWidget):

    def refresh_timeline(self) -> None:
        self.timeline.set_range(self.first_frame, self.last_frame)
        self.timeline.fps = self.fps
        self.timeline.set_frame(self.first_frame)  # Not sure if I want this...

    def __init__(
        self,
        first_frame: int = 1001,
        last_frame: int = 1100,
        fps: float = 24.0,
        parent: QtWidgets.QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.first_frame = first_frame
        self.last_frame = last_frame
        self.fps = fps

        self._create_widgets()
        self._create_layouts()

    def _create_widgets(self) -> None:
        self.layout_main = QtWidgets.QVBoxLayout()
        self.image_view = image_view.ImageView(self)
        self.timeline = timeline.Timeline(
            first_frame=self.first_frame,
            last_frame=self.last_frame,
            fps=self.fps,
            parent=self.parent(),
        )

    def _create_layouts(self) -> None:
        self.setLayout(self.layout_main)
        self.layout_main.addWidget(self.image_view)
        self.layout_main.addWidget(self.timeline)
