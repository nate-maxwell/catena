import logging
from pathlib import Path

from catena import api

CATEGORY = "Noise Pack 01"

logger = logging.getLogger(__name__)


def open_demo_file() -> None:
    fp = Path(__file__).parent / "tile_demo.cg"
    api.open_file(fp)


def initialize() -> None:
    logger.info("Initializing demo plugin")

    api.add_shelf_command("Demo", open_demo_file, "Open\nDemo\nFile")


initialize()
