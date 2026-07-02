from typing import Any
from typing import Optional

import numpy
from PySide6TK import QtGui
from PySide6TK.Nodes import FieldType

from catena.texture import TextureType


class PortDataType(object):
    FLOAT = "float"
    BOOL = "bool"
    INT = "int"
    VECTOR1 = "vector1"
    VECTOR2 = "vector2"
    VECTOR3 = "vector3"
    VECTOR4 = "vector4"
    NORMAL = "normal"
    FLOOD_FILL = "flood_fill"


DATA_TYPE_COLORS: dict[str, QtGui.QColor] = {
    "bool": QtGui.QColor(10, 10, 10),
    "int": QtGui.QColor(0, 128, 255),
    "float": QtGui.QColor(0, 255, 0),
    "vector1": QtGui.QColor(255, 0, 0),
    "vector2": QtGui.QColor(255, 255, 0),
    "vector3": QtGui.QColor(255, 255, 255),
    "vector4": QtGui.QColor(128, 128, 128),
    "normal": QtGui.QColor(0, 0, 255),
    "flood_fill": QtGui.QColor(0, 255, 255),
}

FIELD_PORT_DATA_TYPES: dict[FieldType, str] = {
    FieldType.INT: PortDataType.INT,
    FieldType.FLOAT: PortDataType.FLOAT,
    FieldType.COLOR: PortDataType.VECTOR4,
    FieldType.VEC2: PortDataType.VECTOR2,
    FieldType.VEC3: PortDataType.VECTOR3,
    FieldType.STR: PortDataType.VECTOR4,
    FieldType.CHOICE: PortDataType.VECTOR4,
}

TEXTURE_DATA_TYPES: dict[TextureType, str] = {
    TextureType.ALBEDO: PortDataType.VECTOR4,
    TextureType.AO: PortDataType.VECTOR4,
    TextureType.HEIGHT: PortDataType.VECTOR4,
    TextureType.METALLIC: PortDataType.VECTOR4,
    TextureType.NORMAL: PortDataType.NORMAL,
    TextureType.ROUGHNESS: PortDataType.VECTOR4,
}


def modifier_value_for_data_type(
    data_type: PortDataType, value: Any
) -> Optional[numpy.ndarray]:
    """Convert a field value into the modifier format used by graph nodes."""
    if value is None:
        return None

    if isinstance(value, numpy.ndarray):
        return value.astype(numpy.float32, copy=False)

    if data_type == PortDataType.BOOL:
        return None

    if data_type in (PortDataType.FLOAT, PortDataType.VECTOR1, PortDataType.INT):
        scalar = float(value)
        return numpy.full((1, 1, 1), scalar, dtype=numpy.float32)

    if data_type == PortDataType.VECTOR2:
        x, y = value
        return numpy.array([[[x, y, 0.0, 1.0]]], dtype=numpy.float32)

    if data_type == PortDataType.VECTOR3:
        x, y, z = value
        return numpy.array([[[x, y, z, 1.0]]], dtype=numpy.float32)

    r, g, b, a = value
    return numpy.array([[[r, g, b, a]]], dtype=numpy.float32) / 255.0
