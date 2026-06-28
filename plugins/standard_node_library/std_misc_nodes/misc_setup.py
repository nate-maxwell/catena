import logging

from catena import api
from std_misc_nodes.reroute import RerouteNode

logger = logging.getLogger(__name__)

CATEGORY = "Misc"


def build_registry() -> None:
    logger.info("Registering std misc nodes...")

    api.register_node(CATEGORY, RerouteNode)


def initialize() -> None:

    build_registry()
