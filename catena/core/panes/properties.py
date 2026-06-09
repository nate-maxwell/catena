import broker
from PySide6TK import QtCore
from PySide6TK import QtGui
from PySide6TK import QtWidgets
from PySide6TK import QtWrappers

from catena.core import pubsub
from catena.core.graph.node import BaseNode
from catena.core.graph.node import FieldType
from catena.core.panes.pane import DockablePane
from catena.core.panes.pane import PaneConfig


class PropertiesPane(DockablePane):
    pane_config = PaneConfig(
        title="Properties",
        default_area=QtCore.Qt.DockWidgetArea.RightDockWidgetArea,
    )

    def __init__(self, main_window: QtWidgets.QMainWindow) -> None:
        super().__init__(main_window, self.pane_config)
        self.create_subscriptions()

    def create_subscriptions(self) -> None:
        broker.register_subscriber(pubsub.NODE_DOUBLE_CLICK, self._refresh_properties)

    def create_widgets(self) -> None:
        self.label = QtWidgets.QLabel("", self.content_widget)

    def create_layouts(self) -> None:
        self.content_layout.addWidget(self.label)
        self.content_layout.addStretch()

    def _refresh_properties(self, node: BaseNode) -> None:
        QtWrappers.clear_layout(self.content_layout)

        for definition in node.get_fields():
            row = QtWidgets.QHBoxLayout()
            label = QtWidgets.QLabel(definition.label, self.content_widget)
            row.addWidget(label)
            current_value = node.get_field_value(definition.name)

            if definition.field_type == FieldType.FLOAT:
                widget = QtWidgets.QDoubleSpinBox(self.content_widget)
                widget.setDecimals(3)
                if definition.min_value is not None:
                    widget.setMinimum(definition.min_value)
                if definition.max_value is not None:
                    widget.setMaximum(definition.max_value)
                if current_value is not None:
                    widget.setValue(current_value)
                widget.valueChanged.connect(
                    lambda v, n=definition.name: node.set_field_value(n, v)
                )

            elif definition.field_type == FieldType.INT:
                widget = QtWidgets.QSpinBox(self.content_widget)
                if definition.min_value is not None:
                    widget.setMinimum(int(definition.min_value))
                if definition.max_value is not None:
                    widget.setMaximum(int(definition.max_value))
                if current_value is not None:
                    widget.setValue(current_value)
                widget.valueChanged.connect(
                    lambda v, n=definition.name: node.set_field_value(n, v)
                )

            elif definition.field_type == FieldType.STR:
                widget = QtWidgets.QLineEdit(self.content_widget)
                if current_value is not None:
                    widget.setText(current_value)
                widget.textChanged.connect(
                    lambda v, n=definition.name: node.set_field_value(n, v)
                )

            elif definition.field_type == FieldType.BOOL:
                widget = QtWidgets.QCheckBox(self.content_widget)
                if current_value is not None:
                    widget.setChecked(current_value)
                widget.toggled.connect(
                    lambda v, n=definition.name: node.set_field_value(n, v)
                )

            elif definition.field_type == FieldType.CHOICE:
                widget = QtWidgets.QComboBox(self.content_widget)
                widget.addItems(definition.options)
                if current_value is not None:
                    widget.setCurrentText(current_value)
                widget.currentTextChanged.connect(
                    lambda v, n=definition.name: node.set_field_value(n, v)
                )

            elif definition.field_type in (FieldType.VEC2, FieldType.VEC3):
                widget = QtWidgets.QLineEdit(self.content_widget)
                if current_value is not None:
                    widget.setText(str(current_value))
                widget.textChanged.connect(
                    lambda v, n=definition.name: node.set_field_value(n, v)
                )

            elif definition.field_type == FieldType.COLOR:
                widget = QtWidgets.QPushButton(self.content_widget)
                if current_value is not None:
                    color = QtGui.QColor(*current_value)
                    widget.setStyleSheet(f"background-color: {color.name()};")
                widget.setText("")

            else:
                widget = QtWidgets.QLabel(str(current_value), self.content_widget)

            row.addWidget(widget)
            self.content_layout.addLayout(row)

        self.content_layout.addStretch()
