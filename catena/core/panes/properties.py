import broker
from PySide6TK import QtCore
from PySide6TK import QtWidgets
from PySide6TK import QtWrappers
from PySide6TK.Nodes import FieldDefinition
from PySide6TK.Nodes import FieldType

from catena.core import namespace
from catena.core.panes.pane import DockablePane
from catena.core.panes.pane import PaneConfig
from catena.core.nodes.base import CatenaNode


class PropertiesPane(DockablePane):
    pane_config = PaneConfig(
        title="Properties",
        default_area=QtCore.Qt.DockWidgetArea.RightDockWidgetArea,
    )

    def __post_init__(self) -> None:
        self._create_subscriptions()

    def _create_subscriptions(self) -> None:
        broker.register_subscriber(namespace.NODE_SELECTED, self._refresh_properties)

    def create_widgets(self) -> None:
        self.label = QtWidgets.QLabel("", self.content_widget)

    def create_layouts(self) -> None:
        self.content_layout.addWidget(self.label)
        self.content_layout.addStretch()

    def _refresh_properties(self, node: CatenaNode) -> None:
        QtWrappers.clear_layout(self.content_layout)

        for definition in node.get_fields():
            row = QtWidgets.QHBoxLayout()
            row.setSpacing(6)

            label = QtWidgets.QLabel(definition.label, self.content_widget)
            label.setAlignment(
                QtCore.Qt.AlignmentFlag.AlignRight
                | QtCore.Qt.AlignmentFlag.AlignVCenter
            )
            label.setFixedWidth(100)
            row.addWidget(label)

            if definition.field_type == FieldType.FLOAT:
                widget = self._parse_float(node, definition)
            elif definition.field_type == FieldType.INT:
                widget = self._parse_int(node, definition)
            elif definition.field_type == FieldType.STR:
                widget = self._parse_str(node, definition)
            elif definition.field_type == FieldType.BOOL:
                widget = self._parse_bool(node, definition)
            elif definition.field_type == FieldType.CHOICE:
                widget = self._parse_choice(node, definition)
            elif definition.field_type in (FieldType.VEC2, FieldType.VEC3):
                widget = self._parse_vec(node, definition)
            elif definition.field_type == FieldType.COLOR:
                widget = self._parse_color(node, definition)
            else:
                widget = QtWidgets.QLabel(
                    str(node.get_field_value(definition.name)), self.content_widget
                )

            widget.setSizePolicy(
                QtWidgets.QSizePolicy.Policy.Expanding,
                QtWidgets.QSizePolicy.Policy.Fixed,
            )
            row.addWidget(widget)
            self.content_layout.addLayout(row)

        self.content_layout.addStretch()

    def _parse_float(
        self, node: CatenaNode, definition: FieldDefinition
    ) -> QtWidgets.QWidget:
        current_value = node.get_field_value(definition.name)
        widget = QtWidgets.QDoubleSpinBox(self.content_widget)
        widget.setDecimals(3)
        widget.setSingleStep(0.1)

        if definition.min_value is not None:
            widget.setMinimum(definition.min_value)
        if definition.max_value is not None:
            widget.setMaximum(definition.max_value)
        if current_value is not None:
            widget.setValue(current_value)

        widget.valueChanged.connect(
            lambda v, n=definition.name: node.set_field_value(n, v)
        )
        return widget

    def _parse_int(
        self, node: CatenaNode, definition: FieldDefinition
    ) -> QtWidgets.QWidget:
        current_value = node.get_field_value(definition.name)
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
        return widget

    def _parse_str(
        self, node: CatenaNode, definition: FieldDefinition
    ) -> QtWidgets.QWidget:
        current_value = node.get_field_value(definition.name)
        widget = QtWidgets.QLineEdit(self.content_widget)

        if current_value is not None:
            widget.setText(current_value)

        widget.textChanged.connect(
            lambda v, n=definition.name: node.set_field_value(n, v)
        )
        return widget

    def _parse_bool(
        self, node: CatenaNode, definition: FieldDefinition
    ) -> QtWidgets.QWidget:
        current_value = node.get_field_value(definition.name)
        widget = QtWidgets.QCheckBox(self.content_widget)

        if current_value is not None:
            widget.setChecked(current_value)

        widget.toggled.connect(lambda v, n=definition.name: node.set_field_value(n, v))
        return widget

    def _parse_choice(
        self, node: CatenaNode, definition: FieldDefinition
    ) -> QtWidgets.QWidget:
        current_value = node.get_field_value(definition.name)
        widget = QtWidgets.QComboBox(self.content_widget)
        widget.addItems(definition.options)

        if current_value is not None:
            widget.setCurrentText(current_value)

        widget.currentTextChanged.connect(
            lambda v, n=definition.name: node.set_field_value(n, v)
        )
        return widget

    def _parse_vec(
        self, node: CatenaNode, definition: FieldDefinition
    ) -> QtWidgets.QWidget:
        current_value = node.get_field_value(definition.name)
        widget = QtWidgets.QLineEdit(self.content_widget)

        if current_value is not None:
            widget.setText(str(current_value))

        widget.textChanged.connect(
            lambda v, n=definition.name: node.set_field_value(n, v)
        )
        return widget

    @staticmethod
    def _parse_color(
        node: CatenaNode, definition: FieldDefinition
    ) -> QtWidgets.QWidget:
        current_value = node.get_field_value(definition.name)
        widget = QtWrappers.ColorButton()

        if current_value is not None:
            r, g, b, a = current_value
            widget.set_color(f"#{a:02x}{r:02x}{g:02x}{b:02x}")

        widget.colorChanged.connect(
            lambda c, n=definition.name: node.set_field_value(
                n, (c.red(), c.green(), c.blue(), c.alpha())
            )
        )
        return widget
