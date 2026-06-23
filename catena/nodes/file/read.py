from pathlib import Path
from typing import Optional

import cv2
import numpy
from PySide6TK import QtGui
from PySide6TK.Nodes import FieldDefinition
from PySide6TK.Nodes import FieldType
from PySide6TK.Nodes import PortType

from catena import texture
from catena.nodes.node_gui import CatenaNode
from catena.nodes.node_processor import ProcessorNode


class ReadProcessor(ProcessorNode):
    """A headless processor that reads an modifier file from disk."""

    def __init__(self, filepath: str = "") -> None:
        super().__init__()
        self.filepath = filepath

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        """
        Load an modifier from disk and return it as a float32 array.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Unused; this node
                reads from disk rather than upstream nodes.
        Returns:
            numpy.ndarray | None: A float32 modifier with values in [0, 1],
                or None if the filepath is empty or the file does not exist.
        """
        image = self._load_image()
        if image is None:
            return None
        return image.astype(numpy.float32) / 255.0

    def _load_image(self) -> Optional[numpy.ndarray]:
        """
        Read an modifier file from disk.

        Returns:
            numpy.ndarray | None: The raw uint8 modifier, or None if the file
                cannot be found or read.
        """
        if not self.filepath:
            return None

        img_path = Path(self.filepath)
        if not img_path.exists():
            return None

        image = cv2.imread(str(img_path), cv2.IMREAD_UNCHANGED)
        if image is None:
            return None

        if image.ndim == 3 and image.shape[2] == 3:
            image = texture.bgr_to_rgb(image)

        return image


class ReadNode(CatenaNode):
    """A node that reads an modifier file from disk."""

    _COLOR_HEADER = QtGui.QColor(128, 0, 0)

    def __init__(self) -> None:
        self._processor = ReadProcessor()
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
        self._processor.filepath = self.get_field_value("filepath")
        return self._processor.process(inputs)
