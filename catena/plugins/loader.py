"""
Loads enabled plugins on startup by extending sys.path and running
any startup.py files found in enabled plugin folders.
"""

import importlib.util
import logging
import sys
from pathlib import Path

from catena.plugins.discover import discover_plugins

logger = logging.getLogger(__name__)


def _run_startup(plugin_path: Path) -> None:
    """Run a startup.py file, if it can be found, in the given plugin path."""
    startup = plugin_path / "startup.py"
    if not startup.exists():
        return

    try:
        spec = importlib.util.spec_from_file_location(
            f"{plugin_path.name}.startup", startup
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        logger.info(f"Ran startup.py for plugin: {plugin_path.name}")
    except Exception as e:
        logger.error(f"Failed to run startup.py for plugin {plugin_path.name}: {e}")


def _extend_path_to_plugin(plugin_path: Path) -> None:
    """
    Extend the sys path to the given plugin path, if it hasn't been extended
    already.
    """
    path_str = str(plugin_path)
    if path_str not in sys.path or plugin_path.as_posix() not in sys.path:
        sys.path.insert(0, path_str)
        logger.info(f"Extended sys.path with {plugin_path.name}")


def load_plugins() -> None:
    """
    For each enabled plugin:
    - Add the plugin folder to sys.path so it can be imported as a library
    - Run startup.py if present
    """
    plugins = discover_plugins()

    for descriptor in plugins:
        if not descriptor.enabled:
            continue

        plugin_path = descriptor.path
        _extend_path_to_plugin(plugin_path)
        _run_startup(plugin_path)
