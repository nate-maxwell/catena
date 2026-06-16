from PySide6TK import QtGui


class PortDataType(object):
    VECTOR1 = "vector1"
    VECTOR2 = "vector2"
    VECTOR3 = "vector3"
    NORMAL = "normal"


DATA_TYPE_COLORS: dict[str, QtGui.QColor] = {
    "vector1": QtGui.QColor(255, 230, 0),
    "vector2": QtGui.QColor(230, 255, 0),
    "vector3": QtGui.QColor(200, 200, 200),
    "normal": QtGui.QColor(0, 0, 255),
}
