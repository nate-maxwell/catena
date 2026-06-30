import logging

from std_convert_nodes import convert_setup
from std_graph_nodes import graph_nodes_setup
from std_flood_fill_nodes import flood_fill_setup
from std_generate_nodes import generator_setup
from std_math_nodes import math_setup
from std_modifier_nodes import modifier_setup
from std_subgraph_nodes import subgraph_setup
from std_transform_nodes import transform_setup
from std_misc_nodes import misc_setup

logger = logging.getLogger(__name__)


def build_standard_node_library() -> None:
    logger.info("-" * 30)
    logger.info("Registering standard node library")

    graph_nodes_setup.initialize()
    convert_setup.initialize()
    flood_fill_setup.initialize()
    generator_setup.initialize()
    math_setup.initialize()
    misc_setup.initialize()
    modifier_setup.initialize()
    subgraph_setup.initialize()
    transform_setup.initialize()

    logger.info("-" * 30)


build_standard_node_library()
