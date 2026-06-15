from catena.core.nodes.base import CatenaNode
from catena.core.nodes.generator import IMAGE_NODE_COLOR


class PreviewNode(CatenaNode):

    _COLOR_HEADER = IMAGE_NODE_COLOR

    def __init__(self, title: str, width: int = 160, body_height: int = 40) -> None:
        super().__init__(title, width, body_height)
