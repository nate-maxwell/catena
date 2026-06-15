from pathlib import Path
from typing import Optional

import broker
import cv2
import numpy
from PySide6TK.Nodes.node import FieldDefinition
from PySide6TK.Nodes.node import FieldType
from PySide6TK.Nodes.node import Port
from PySide6TK.Nodes.node import PortType

from catena.core import namespace
from catena.core import texture
from catena.core.nodes.base import CatenaNode
from catena.core.nodes.file import IMAGE_NODE_COLOR

_EXTENSIONS = {
    "PNG": ".png",
    "JPEG": ".jpg",
    "BMP": ".bmp",
    "TIFF": ".tiff",
    "WEBP": ".webp",
}


class WriteNode(CatenaNode):
    """
    A node that writes its input image to disk.
    Additionally, will update the model viewer.
    """

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(
        self,
        title: str,
        texture_type: texture.TextureType,
        width: int = 160,
        body_height: int = 40,
    ) -> None:
        super().__init__(title, width, body_height)
        self._texture_type = texture_type
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

        # This might need to be adjusted to output uint32 in the future...
        output = numpy.clip(image * 255.0, 0, 255).astype(numpy.uint8)

        if output.ndim == 3 and output.shape[2] == 3:
            output = texture.rgb_to_bgr(output)

        return cv2.imwrite(str(path), output)

    def on_input_connection_changed(self, port: Port) -> None:
        self._cached_value = None
        self._emit_preview_update()

    def _emit_preview_update(self) -> None:
        """
        Evaluate this node's input and notify the model preview if a result is
        available.
        """
        image = self.evaluate()

        broker.emit(
            namespace.MODEL_UPDATED_TEXTURE,
            image=image,
            texture_type=self._texture_type,
        )
