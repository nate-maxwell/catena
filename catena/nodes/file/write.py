from pathlib import Path
from typing import Optional

import broker
import cv2
import numpy
from PySide6TK.Nodes import FieldDefinition
from PySide6TK.Nodes import FieldType
from PySide6TK.Nodes import Port
from PySide6TK.Nodes import PortType

from catena import namespace
from catena import texture
from catena.nodes.node_gui import CatenaNode
from catena.nodes.data import DATA_TYPE_COLORS
from catena.nodes.data import PortDataType
from catena.nodes.file import IMAGE_NODE_COLOR
from catena.nodes.node_processor import ProcessorNode

_EXTENSIONS = {
    "PNG": ".png",
    "JPEG": ".jpg",
    "BMP": ".bmp",
    "TIFF": ".tiff",
    "WEBP": ".webp",
}


class WriteProcessor(ProcessorNode):
    """A headless processor that writes an modifier to disk."""

    def __init__(
        self,
        filepath: str = "",
        file_type: str = "PNG",
    ) -> None:
        super().__init__()
        self.filepath = filepath
        self.file_type = file_type

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        """
        Pass the input modifier through unchanged.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Expects key "Input"
                containing a float32 modifier.
        Returns:
            numpy.ndarray | None: The input modifier unchanged.
        """
        return inputs.get("Input")

    def write_image(self, image: Optional[numpy.ndarray]) -> bool:
        """
        Write an modifier array to disk.

        Args:
            image (numpy.ndarray | None): The float32 modifier to write.
        Returns:
            bool: True if the modifier was written successfully, False otherwise.
        """
        if image is None:
            return False

        if not self.filepath:
            return False

        path = Path(self.filepath)
        extension = _EXTENSIONS[self.file_type]
        path = path.with_suffix(extension)

        path.parent.mkdir(parents=True, exist_ok=True)

        output = numpy.clip(image * 255.0, 0, 255).astype(numpy.uint8)

        if output.ndim == 3 and output.shape[2] == 4:
            output = output[:, :, :3]

        return cv2.imwrite(str(path), output)


class WriteNode(CatenaNode):
    """
    A node that writes its input modifier to disk.
    Additionally, will update the model viewer.
    """

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(
        self,
        title: str,
        texture_type: texture.TextureType,
        data_type: str = PortDataType.VECTOR4,
        width: int = 160,
        body_height: int = 40,
    ) -> None:
        self._processor = WriteProcessor()
        self._data_type = data_type
        self._texture_type = texture_type
        super().__init__(title, width, body_height)
        broker.register_subscriber(namespace.NODE_WRITE_FILE, self.write_image)

    def _build(self) -> None:
        # self.port_in = self.add_port(PortType.INPUT, "Input")
        self.port_in = self.add_port(PortType.INPUT, "Input", self._data_type)
        self.port_in.set_color(DATA_TYPE_COLORS[self._data_type])

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
            bool: True if the modifier was written successfully, False otherwise.
        """
        self._processor.filepath = self.get_field_value("filepath")
        self._processor.file_type = self.get_field_value("file_type")
        return self._processor.write_image(self.evaluate())

    def on_input_connection_changed(self, port: Port) -> None:
        self._cached_value = None
        self._emit_preview_update()

    def _emit_preview_update(self) -> None:
        """
        Evaluate this node's input and notify the model preview if a result is
        available.
        """
        broker.emit(
            namespace.MODEL_UPDATED_TEXTURE,
            image=self.evaluate(),
            texture_type=self._texture_type,
        )
