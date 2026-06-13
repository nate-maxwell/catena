from pathlib import Path
from typing import Optional

import broker
import cv2
import numpy
from PySide6TK import QtGui
from PySide6TK.Nodes.node import FieldDefinition
from PySide6TK.Nodes.node import FieldType
from PySide6TK.Nodes.node import PortType

from catena.core import namespace
from catena.core.nodes.base import CatenaNode

NODE_TYPE = "Write"

_EXTENSIONS = {
    "PNG": ".png",
    "JPEG": ".jpg",
    "BMP": ".bmp",
    "TIFF": ".tiff",
    "WEBP": ".webp",
}


class WriteNode(CatenaNode):
    """A node that writes its input image to disk."""

    _COLOR_HEADER = QtGui.QColor(0, 0, 0)

    def __init__(self) -> None:
        super().__init__(title="Write", width=200, body_height=40)
        broker.register_subscriber(namespace.NODE_WRITE_FILE, self.write_image)

    def _build(self) -> None:
        self.port_in = self.add_port(PortType.INPUT, "Input")

        self.add_field(
            FieldDefinition(
                name="filepath",
                label="Filepath",
                field_type=FieldType.STR,
                default="",
            )
        )
        self.add_field(
            FieldDefinition(
                name="file_type",
                label="File Type",
                field_type=FieldType.CHOICE,
                default="PNG",
                options=list(_EXTENSIONS.keys()),
            )
        )

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        return inputs.get("Input")

    def write_image(self) -> bool:
        """
        Evaluate this node's input and write the result to disk.

        Returns:
            bool: True if the image was written successfully, False otherwise.
        """
        image = self.evaluate()
        if image is None:
            return False

        filepath = self.get_field_value("filepath")
        if not filepath:
            return False

        path = Path(filepath)
        extension = _EXTENSIONS[self.get_field_value("file_type")]
        path = path.with_suffix(extension)

        path.parent.mkdir(parents=True, exist_ok=True)
        return cv2.imwrite(str(path), image)
