from pathlib import Path
from typing import Optional

import broker
import cv2
import numpy

from catena import api
from catena import namespace
from std_graph_nodes import IMAGE_NODE_COLOR

_EXTENSIONS = {
    "PNG": ".png",
    "JPEG": ".jpg",
    "BMP": ".bmp",
    "TIFF": ".tiff",
    "WEBP": ".webp",
}

_TEXTURE_TYPES: dict[str, api.TextureType] = {t.value: t for t in api.TextureType}


class WriteNode(api.CatenaNode):
    """
    A node that writes its input image to disk and updates the model viewer.
    The title updates to reflect the selected texture type.
    """

    _COLOR_HEADER = IMAGE_NODE_COLOR
    WRITE_NODE_PREVIEW = True

    def __init__(
        self,
        data_type: str = api.PortDataType.VECTOR4,
        width: int = 160,
        body_height: int = 40,
    ) -> None:
        self._data_type = data_type
        self._texture_type = api.TextureType.ALBEDO
        super().__init__("Output", width, body_height)
        broker.register_subscriber(namespace.NODE_WRITE_FILE, self.write_image)

    def _build(self) -> None:
        self.port_in = self.add_port(api.PortType.INPUT, "Input", self._data_type)
        self.port_in.set_color(api.DATA_TYPE_COLORS[self._data_type])

        self.add_field(
            api.FieldDefinition(
                name="texture_type",
                label="Texture Type",
                field_type=api.FieldType.CHOICE,
                default="Albedo",
                options=list(_TEXTURE_TYPES.keys()),
            )
        )
        self.add_field(
            api.FieldDefinition(
                name="filepath",
                label="Filepath",
                field_type=api.FieldType.STR,
                default="",
            )
        )
        self.add_field(
            api.FieldDefinition(
                name="file_type",
                label="File Type",
                field_type=api.FieldType.CHOICE,
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
        filepath = self.get_field_value("filepath")
        file_type = self.get_field_value("file_type")
        if image is None:
            return False

        if not filepath:
            return False

        path = Path(filepath)
        extension = _EXTENSIONS[file_type]
        path = path.with_suffix(extension)

        path.parent.mkdir(parents=True, exist_ok=True)

        output = numpy.clip(image * 255.0, 0, 255).astype(numpy.uint8)

        if output.ndim == 3 and output.shape[2] == 4:
            output = output[:, :, :3]

        return cv2.imwrite(str(path), output)

    def _on_field_changed(self, node: api.CatenaNode) -> None:
        texture_type_name = self.get_field_value("texture_type")
        self._texture_type = _TEXTURE_TYPES.get(
            texture_type_name, api.TextureType.ALBEDO
        )
        self.title = f"{texture_type_name} Output"

        data_type = api.TEXTURE_DATA_TYPES.get(
            self._texture_type, api.PortDataType.VECTOR4
        )
        if self.port_in.data_type != data_type:
            self.remove_port(self.port_in)
            self.port_in = self.add_port(api.PortType.INPUT, "Input", data_type)
            self.port_in.set_color(api.DATA_TYPE_COLORS[data_type])

        self.update()
        self._emit_preview_update()
        super()._on_field_changed(node)

    def on_input_connection_changed(self, port: api.Port) -> None:
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
