from __future__ import annotations

import time
from typing import Optional

import broker
from PySide6 import QtCore
from PySide6 import QtWidgets

from catena import namespace
from catena.api import CatenaNode

NODE_EVALUATED = "node.evaluated"

# ── monkey-patch ─────────────────────────────────────────────────────────────

_original_evaluate = CatenaNode.evaluate


def _instrumented_evaluate(self: CatenaNode) -> Optional[object]:
    if self._cached_value is None:
        inputs = self.get_inputs()
        t0 = time.perf_counter()
        self._cached_value = self.process(inputs)
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        broker.emit(
            NODE_EVALUATED,
            node_title=self.title,
            elapsed_ms=elapsed_ms,
        )
    return self._cached_value


CatenaNode.evaluate = _instrumented_evaluate

# ── widgets ───────────────────────────────────────────────────────────────────


class _NodeStatRow(QtWidgets.QWidget):
    """A single row showing a node title and its last evaluation time."""

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(8, 2, 8, 2)
        layout.setSpacing(8)

        self.label_name = QtWidgets.QLabel()
        self.label_name.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Fixed,
        )

        self.label_time = QtWidgets.QLabel()
        self.label_time.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        self.label_time.setFixedWidth(64)

        layout.addWidget(self.label_name)
        layout.addWidget(self.label_time)

    def set_data(self, name: str, ms: float, is_slowest: bool) -> None:
        self.label_name.setText(name)
        self.label_time.setText(f"{ms:.1f} ms")
        color = "#e05555" if is_slowest else "#aaaaaa"
        self.label_time.setStyleSheet(f"color: {color};")


class GraphStatsWidget(QtWidgets.QWidget):
    """
    A widget that displays per-node evaluation times and total graph cost.
    Monkey-patches CatenaNode.evaluate() on import so no changes to the
    core codebase are required.
    """

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)

        self._stats: dict[str, float] = {}
        self._row_widgets: list[_NodeStatRow] = []

        self._build_ui()

        broker.register_subscriber(NODE_EVALUATED, self._on_node_evaluated)
        broker.register_subscriber(namespace.FILE_NEW, self._reset_stats)
        broker.register_subscriber(namespace.FILE_LOAD, self._reset_stats)
        broker.register_subscriber(
            namespace.GRAPH_OPEN_SUBGRAPH, self._reset_stats_for_graph
        )

    def _build_ui(self) -> None:
        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        header = QtWidgets.QWidget()
        header.setFixedHeight(32)
        header.setStyleSheet("background: #2a2a2a;")
        header_layout = QtWidgets.QHBoxLayout(header)
        header_layout.setContentsMargins(8, 0, 8, 0)

        lbl_node = QtWidgets.QLabel("Node")
        lbl_node.setStyleSheet("color: #888; font-size: 11px;")
        lbl_time = QtWidgets.QLabel("Time")
        lbl_time.setStyleSheet("color: #888; font-size: 11px;")
        lbl_time.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        lbl_time.setFixedWidth(64)

        header_layout.addWidget(lbl_node)
        header_layout.addWidget(lbl_time)
        root.addWidget(header)

        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)

        self._rows_widget = QtWidgets.QWidget()
        self._rows_layout = QtWidgets.QVBoxLayout(self._rows_widget)
        self._rows_layout.setContentsMargins(0, 4, 0, 4)
        self._rows_layout.setSpacing(0)
        self._rows_layout.addStretch()

        scroll.setWidget(self._rows_widget)
        root.addWidget(scroll)

        footer = QtWidgets.QWidget()
        footer.setFixedHeight(36)
        footer.setStyleSheet("background: #222; border-top: 1px solid #333;")
        footer_layout = QtWidgets.QHBoxLayout(footer)
        footer_layout.setContentsMargins(8, 0, 8, 0)

        lbl_total_title = QtWidgets.QLabel("Total")
        lbl_total_title.setStyleSheet(
            "color: #ccc; font-weight: bold; font-size: 11px;"
        )

        self._lbl_total = QtWidgets.QLabel("— ms")
        self._lbl_total.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        self._lbl_total.setFixedWidth(64)
        self._lbl_total.setStyleSheet(
            "color: #ccc; font-weight: bold; font-size: 11px;"
        )

        footer_layout.addWidget(lbl_total_title)
        footer_layout.addWidget(self._lbl_total)
        root.addWidget(footer)

    # ── broker callbacks ─────────────────────────────────────────────────────

    def _on_node_evaluated(self, node_title: str, elapsed_ms: float) -> None:
        self._stats[node_title] = elapsed_ms
        self._refresh()

    def _reset_stats(self) -> None:
        self._stats.clear()
        self._refresh()

    def _reset_stats_for_graph(self, file_path: object) -> None:
        self._stats.clear()
        self._refresh()

    # ── rendering ────────────────────────────────────────────────────────────

    def _refresh(self) -> None:
        if not self._stats:
            for row in self._row_widgets:
                row.setVisible(False)
            self._lbl_total.setText("— ms")
            return

        items = sorted(self._stats.items(), key=lambda x: x[1], reverse=True)
        total = sum(ms for _, ms in items)
        slowest_name = items[0][0]

        while len(self._row_widgets) < len(items):
            row = _NodeStatRow()
            self._rows_layout.insertWidget(self._rows_layout.count() - 1, row)
            self._row_widgets.append(row)

        for i, row in enumerate(self._row_widgets):
            row.setVisible(i < len(items))

        for i, (name, ms) in enumerate(items):
            self._row_widgets[i].set_data(name, ms, name == slowest_name)

        self._lbl_total.setText(f"{total:.1f} ms")
