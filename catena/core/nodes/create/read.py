from pathlib import Path
from typing import Optional

import cv2
import numpy
from PySide6TK.Nodes import FieldDefinition
from PySide6TK.Nodes import FieldType
from PySide6TK.Nodes import PortType

from catena.core.nodes.base import CatenaNode
from catena.core.nodes.create import IMAGE_NODE_COLOR


class ReadNode(CatenaNode):

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        super().__init__(title="Read", width=180, body_height=40)

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
        return self._load_image()

    def _load_image(self) -> Optional[numpy.ndarray]:
        filepath = self.get_field_value("filepath")
        if not filepath:
            return None

        img_path = Path(filepath)
        if img_path.exists():
            return cv2.imread(str(img_path))

        return None
