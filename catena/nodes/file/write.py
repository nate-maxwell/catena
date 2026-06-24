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
from catena.nodes.node_gui import CatenaNode
from catena.nodes.data import DATA_TYPE_COLORS
from catena.nodes.data import PortDataType
from catena.nodes.file import IMAGE_NODE_COLOR
from catena.nodes.node_processor import ProcessorNode
from catena.texture import TextureType
from catena.nodes.data import TEXTURE_DATA_TYPES

_EXTENSIONS = {
    "PNG": ".png",
    "JPEG": ".jpg",
    "BMP": ".bmp",
    "TIFF": ".tiff",
    "WEBP": ".webp",
}

_TEXTURE_TYPES: dict[str, TextureType] = {t.value: t for t in TextureType}


class WriteProcessor(ProcessorNode):
    """A headless processor that writes an image to disk."""

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
        Pass the input image through unchanged.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Expects key "Input"
                containing a float32 image.
        Returns:
            numpy.ndarray | None: The input image unchanged.
        """
        return inputs.get("Input")

    def write_image(self, image: Optional[numpy.ndarray]) -> bool:
        """
        Write an image array to disk.

        Args:
            image (numpy.ndarray | None): The float32 image to write.
        Returns:
            bool: True if the image was written successfully, False otherwise.
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
    A node that writes its input image to disk and updates the model viewer.
    The title updates to reflect the selected texture type.
    """

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(
        self,
        data_type: str = PortDataType.VECTOR4,
        width: int = 160,
        body_height: int = 40,
    ) -> None:
        self._processor = WriteProcessor()
        self._data_type = data_type
        self._texture_type = TextureType.ALBEDO
        super().__init__("Output", width, body_height)
        broker.register_subscriber(namespace.NODE_WRITE_FILE, self.write_image)

    def _build(self) -> None:
        self.port_in = self.add_port(PortType.INPUT, "Input", self._data_type)
        self.port_in.set_color(DATA_TYPE_COLORS[self._data_type])

        self.add_field(
            FieldDefinition(
                name="texture_type",
                label="Texture Type",
                field_type=FieldType.CHOICE,
                default="Albedo",
                options=list(_TEXTURE_TYPES.keys()),
            )
        )
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
        self._processor.filepath = self.get_field_value("filepath")
        self._processor.file_type = self.get_field_value("file_type")
        return self._processor.write_image(self.evaluate())

    def _on_field_changed(self, node: "CatenaNode") -> None:
        texture_type_name = self.get_field_value("texture_type")
        self._texture_type = _TEXTURE_TYPES.get(texture_type_name, TextureType.ALBEDO)
        self.title = f"{texture_type_name} Output"

        data_type = TEXTURE_DATA_TYPES.get(self._texture_type, PortDataType.VECTOR4)
        if self.port_in.data_type != data_type:
            self.remove_port(self.port_in)
            self.port_in = self.add_port(PortType.INPUT, "Input", data_type)
            self.port_in.set_color(DATA_TYPE_COLORS[data_type])

        self.update()
        self._emit_preview_update()
        super()._on_field_changed(node)

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
