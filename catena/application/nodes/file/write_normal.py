from catena.application import texture
from catena.application.nodes.data import PortDataType
from catena.application.nodes.file import IMAGE_NODE_COLOR
from catena.application.nodes.file.write import WriteNode


class NormalNode(WriteNode):

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self) -> None:
        super().__init__(
            title="Normal",
            texture_type=texture.TextureType.NORMAL,
            data_type=PortDataType.NORMAL,
        )
