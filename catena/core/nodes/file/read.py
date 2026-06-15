from pathlib import Path
from typing import Optional

import cv2
import numpy
from PySide6TK import QtGui
from PySide6TK.Nodes import FieldDefinition
from PySide6TK.Nodes import FieldType
from PySide6TK.Nodes import PortType

from catena.core.nodes.base import CatenaNode


class ReadNode(CatenaNode):

    _COLOR_HEADER = QtGui.QColor(128, 0, 0)

    def __init__(self) -> None:
        super().__init__(title="Read")

    def _build(self) -> None:
        self.port_out = self.add_port(PortType.OUTPUT, "File")

        self.add_field(
            FieldDefinition(
                name="filepath",
                label="Filepath",
                field_type=FieldType.STR,
                default="",
            )
        )

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        image = self._load_image()
        if image is None:
            return None
        return image.astype(numpy.float32) / 255.0

    def _load_image(self) -> Optional[numpy.ndarray]:
        filepath = self.get_field_value("filepath")
        if not filepath:
            return None

        img_path = Path(filepath)
        if img_path.exists():
            return cv2.imread(str(img_path))

        return None
