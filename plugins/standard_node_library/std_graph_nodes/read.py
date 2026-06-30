from pathlib import Path
from typing import Optional

import cv2
import numpy

from catena import api
from std_graph_nodes import IMAGE_NODE_COLOR


class ReadNode(api.CatenaNode):
    """A node that reads a texture file from disk."""

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        super().__init__(title="Read")

    def _build(self) -> None:
        self.port_out = self.add_port(api.PortType.OUTPUT, "File")

        self.add_field(
            api.FieldDefinition(
                name="filepath",
                label="Filepath",
                field_type=api.FieldType.STR,
                default="",
            )
        )

    def _load_image(self) -> Optional[numpy.ndarray]:
        """
        Read a texture file from disk.

        Returns:
            numpy.ndarray | None: The raw uint8 texture, or None if the file
                cannot be found or read.
        """
        filepath = self.get_field_value("filepath")
        if not filepath:
            return None

        img_path = Path(filepath)
        if not img_path.exists():
            return None

        image = cv2.imread(str(img_path), cv2.IMREAD_UNCHANGED)
        if image is None:
            return None

        if image.ndim == 3 and image.shape[2] == 3:
            image = api.bgr_to_rgb(image)

        return image

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        """
        Load a texture from disk and return it as a float32 array.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Unused; this node
                reads from disk rather than upstream nodes.
        Returns:
            numpy.ndarray | None: A float32 texture with values in [0, 1],
                or None if the filepath is empty or the file does not exist.
        """
        filepath = self.get_field_value("filepath")
        image = self._load_image()
        if image is None:
            return None

        return image.astype(numpy.float32) / 255.0
