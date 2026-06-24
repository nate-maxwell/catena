from PySide6TK import QtGui

from catena.texture import TextureType


class PortDataType(object):
    VECTOR1 = "vector1"
    VECTOR2 = "vector2"
    VECTOR3 = "vector3"
    VECTOR4 = "vector4"
    NORMAL = "normal"
    FLOOD_FILL = "flood_fill"


DATA_TYPE_COLORS: dict[str, QtGui.QColor] = {
    "vector1": QtGui.QColor(255, 0, 0),
    "vector2": QtGui.QColor(255, 255, 0),
    "vector3": QtGui.QColor(255, 255, 255),
    "vector4": QtGui.QColor(128, 128, 128),
    "normal": QtGui.QColor(0, 0, 255),
    "flood_fill": QtGui.QColor(0, 255, 0),
}

TEXTURE_DATA_TYPES: dict[TextureType, str] = {
    TextureType.ALBEDO: PortDataType.VECTOR4,
    TextureType.AO: PortDataType.VECTOR4,
    TextureType.HEIGHT: PortDataType.VECTOR4,
    TextureType.METALLIC: PortDataType.VECTOR4,
    TextureType.NORMAL: PortDataType.NORMAL,
    TextureType.ROUGHNESS: PortDataType.VECTOR4,
}
