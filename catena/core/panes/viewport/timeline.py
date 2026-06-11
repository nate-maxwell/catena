from __future__ import annotations

from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets

from catena.core.panes.pane import DockablePane
from catena.core.panes.pane import PaneConfig


class Timeline(QtWidgets.QWidget):
    """
    A Nuke-style timeline widget with transport controls and a draggable playhead.

    Args:
        first_frame (int): The first frame of the range.
        last_frame (int): The last frame of the range.
        fps (float): Frames per second for playback.
        parent (QtWidgets.QWidget | None): Optional parent widget.

    Attributes:
        first_frame (int): First frame of the range.
        last_frame (int): Last frame of the range.
        fps (float): Playback speed in frames per second.

    Signals:
        frame_changed (int): Emitted when the current frame changes.
    """

    frame_changed = QtCore.Signal(int)

    _COLOR_BG: QtGui.QColor = QtGui.QColor(40, 40, 40)
    _COLOR_TRACK: QtGui.QColor = QtGui.QColor(30, 30, 30)
    _COLOR_RANGE: QtGui.QColor = QtGui.QColor(100, 120, 220, 60)
    _COLOR_HEAD: QtGui.QColor = QtGui.QColor(100, 120, 220)
    _COLOR_TICK: QtGui.QColor = QtGui.QColor(80, 80, 80)
    _COLOR_TICK_LABEL: QtGui.QColor = QtGui.QColor(120, 120, 120)
    _TRACK_HEIGHT: int = 32
    _HEAD_WIDTH: int = 2

    def __init__(
        self,
        first_frame: int = 1,
        last_frame: int = 100,
        fps: float = 24.0,
        parent: QtWidgets.QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.first_frame = first_frame
        self.last_frame = last_frame
        self.fps = fps
        self._frame: int = first_frame
        self._play_dir: int = 0
        self._dragging: bool = False

        self._timer = QtCore.QTimer(self)
        self._timer.setInterval(int(1000 / fps))
        self._timer.timeout.connect(self._on_tick)

        self._create_widgets()
        self._create_layouts()
        self._create_connections()
        self.setMinimumSize(0, 0)

    def _create_widgets(self) -> None:
        self._track = _TrackWidget(self)

        self._btn_start = self._make_btn("<<", "To start")
        self._btn_prev = self._make_btn("<", "Previous frame")
        self._btn_back = self._make_btn("<|", "Play backwards", checkable=True)
        self._btn_stop = self._make_btn("■", "Stop")
        self._btn_play = self._make_btn("|>", "Play forwards", checkable=True)
        self._btn_next = self._make_btn(">", "Next frame")
        self._btn_end = self._make_btn(">>", "To end")

        self._frame_display = QtWidgets.QLabel(str(self._frame))
        self._frame_display.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self._frame_display.setMinimumWidth(48)

        self._total_display = QtWidgets.QLabel(str(self.last_frame))
        self._total_display.setStyleSheet("color: #666;")

    def _create_layouts(self) -> None:
        controls = QtWidgets.QHBoxLayout()
        controls.setSpacing(3)
        controls.setContentsMargins(0, 0, 0, 0)
        controls.addStretch()
        for w in (
            self._btn_start,
            self._btn_prev,
            self._btn_back,
            self._btn_stop,
            self._btn_play,
            self._btn_next,
            self._btn_end,
        ):
            controls.addWidget(w)

        sep = QtWidgets.QFrame()
        sep.setFrameShape(QtWidgets.QFrame.Shape.VLine)
        sep.setStyleSheet("color: #444;")
        controls.addWidget(sep)
        controls.addWidget(self._frame_display)
        controls.addWidget(QtWidgets.QLabel("/"))
        controls.addWidget(self._total_display)
        controls.addStretch()

        root = QtWidgets.QVBoxLayout(self)
        root.setSpacing(4)
        root.setContentsMargins(6, 6, 6, 6)
        root.addWidget(self._track)
        root.addLayout(controls)

    def _create_connections(self) -> None:
        self._btn_start.clicked.connect(
            lambda: (self.stop(), self.set_frame(self.first_frame))
        )
        self._btn_end.clicked.connect(
            lambda: (self.stop(), self.set_frame(self.last_frame))
        )
        self._btn_prev.clicked.connect(
            lambda: (self.stop(), self.set_frame(self._frame - 1))
        )
        self._btn_next.clicked.connect(
            lambda: (self.stop(), self.set_frame(self._frame + 1))
        )
        self._btn_stop.clicked.connect(self.stop)
        self._btn_play.clicked.connect(
            lambda checked: self._start_playback(1) if checked else self.stop()
        )
        self._btn_back.clicked.connect(
            lambda checked: self._start_playback(-1) if checked else self.stop()
        )
        self._track.seek_requested.connect(self.set_frame)

    @property
    def frame(self) -> int:
        """
        The current frame.

        Returns:
            int: Current frame.
        """
        return self._frame

    def set_frame(self, frame: int) -> None:
        """
        Set the current frame and emit frame_changed.

        Args:
            frame (int): The frame to set.
        """
        self._frame = max(self.first_frame, min(self.last_frame, frame))
        self._frame_display.setText(str(self._frame))
        self._track.update()
        self.frame_changed.emit(self._frame)

    def set_range(self, first: int, last: int) -> None:
        """
        Update the frame range.

        Args:
            first (int): New first frame.
            last (int): New last frame.
        """
        self.first_frame = first
        self.last_frame = last
        self._total_display.setText(str(last))
        self.set_frame(max(self.first_frame, min(self.last_frame, self._frame)))

    def stop(self) -> None:
        """Stop playback."""
        self._play_dir = 0
        self._timer.stop()
        self._btn_play.setChecked(False)
        self._btn_back.setChecked(False)

    def _make_btn(
        self,
        text: str,
        tooltip: str,
        checkable: bool = False,
    ) -> QtWidgets.QPushButton:
        btn = QtWidgets.QPushButton(text)
        btn.setToolTip(tooltip)
        btn.setCheckable(checkable)
        btn.setFixedSize(26, 26)
        return btn

    def _start_playback(self, direction: int) -> None:
        self._play_dir = direction
        self._btn_play.setChecked(direction == 1)
        self._btn_back.setChecked(direction == -1)
        self._timer.start()

    def _on_tick(self) -> None:
        next_frame = self._frame + self._play_dir
        if next_frame > self.last_frame or next_frame < self.first_frame:
            self.stop()
            return
        self.set_frame(next_frame)


class _TrackWidget(QtWidgets.QWidget):
    """
    The track area of the timeline — draws ticks, range fill, and playhead.

    Args:
        timeline (Timeline): The parent Timeline widget.
    """

    seek_requested = QtCore.Signal(int)

    def __init__(self, timeline: Timeline) -> None:
        super().__init__(timeline)
        self._timeline = timeline
        self.setFixedHeight(timeline._TRACK_HEIGHT)
        self.setMinimumWidth(0)
        self.setCursor(QtCore.Qt.CursorShape.SizeHorCursor)

    def _frame_to_x(self, frame: int) -> float:
        span = self._timeline.last_frame - self._timeline.first_frame
        if span == 0:
            return 0.0
        return (frame - self._timeline.first_frame) / span * self.width()

    def _x_to_frame(self, x: int) -> int:
        span = self._timeline.last_frame - self._timeline.first_frame
        if span == 0:
            return self._timeline.first_frame
        ratio = max(0.0, min(1.0, x / self.width()))
        return round(ratio * span + self._timeline.first_frame)

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.seek_requested.emit(self._x_to_frame(event.position().toPoint().x()))

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        if event.buttons() & QtCore.Qt.MouseButton.LeftButton:
            self.seek_requested.emit(self._x_to_frame(event.position().toPoint().x()))

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        tl = self._timeline
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing, False)
        w, h = self.width(), self.height()

        painter.fillRect(0, 0, w, h, tl._COLOR_TRACK)

        head_x = int(self._frame_to_x(tl.frame))
        painter.fillRect(0, 0, head_x, h, tl._COLOR_RANGE)

        span = tl.last_frame - tl.first_frame
        step = 10 if span <= 200 else 25
        painter.setPen(QtGui.QPen(tl._COLOR_TICK, 1))
        font = painter.font()
        font.setPointSize(7)
        painter.setFont(font)

        for f in range(tl.first_frame, tl.last_frame + 1):
            if f % step == 0 or f == tl.first_frame or f == tl.last_frame:
                x = int(self._frame_to_x(f))
                major = f % (step * 2) == 0 or f == tl.first_frame or f == tl.last_frame
                tick_top = int(h * 0.35) if major else int(h * 0.6)
                painter.setPen(QtGui.QPen(tl._COLOR_TICK, 1))
                painter.drawLine(x, tick_top, x, h)
                if major:
                    painter.setPen(tl._COLOR_TICK_LABEL)
                    painter.drawText(
                        QtCore.QRect(x - 16, 0, 32, tick_top - 2),
                        QtCore.Qt.AlignmentFlag.AlignHCenter
                        | QtCore.Qt.AlignmentFlag.AlignBottom,
                        str(f),
                    )

        head_pen = QtGui.QPen(tl._COLOR_HEAD, tl._HEAD_WIDTH)
        painter.setPen(head_pen)
        painter.drawLine(head_x, 0, head_x, h)

        triangle = QtGui.QPolygon(
            [
                QtCore.QPoint(head_x - 5, 0),
                QtCore.QPoint(head_x + 5, 0),
                QtCore.QPoint(head_x, 6),
            ]
        )
        painter.setBrush(QtGui.QBrush(tl._COLOR_HEAD))
        painter.setPen(QtCore.Qt.PenStyle.NoPen)
        painter.drawPolygon(triangle)

        painter.end()
