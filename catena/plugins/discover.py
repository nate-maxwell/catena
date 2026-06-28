from pathlib import Path

import core_utils.env
import core_utils.structured

from catena import appdata
from catena.plugins import plugin_record
from catena.plugins.descriptor import PluginDescriptor

CONFIG_FILE = "plugin.json"


def discover_client_plugins() -> list[PluginDescriptor]:
    """Returns a list of plugin descriptions for all built-in Catena plugins."""
    client_plugin_path = appdata.BUILT_IN_PLUGINS_PATH
    if not client_plugin_path.exists():
        return []

    plugins = []
    for plugin_path in client_plugin_path.iterdir():
        if not plugin_path.is_dir():
            continue

        cfg = Path(plugin_path, CONFIG_FILE)
        if cfg.exists():
            cfg_data = core_utils.structured.import_data_from_json(cfg)
            if cfg_data is None:
                continue

            plugin_data = PluginDescriptor(path=plugin_path, **cfg_data)
            plugins.append(plugin_data)

    return plugins


def discover_user_plugins() -> list[PluginDescriptor]:
    """Returns a list of plugin descriptions for all user-made Catena plugins."""
    user_plugin_paths = core_utils.env.get_list(appdata.PLUGINS_ENV_VAR)
    if user_plugin_paths is None:
        return []

    plugins = []
    for plugin_dir in user_plugin_paths:
        plugin_path = Path(plugin_dir)
        if not plugin_path.is_dir():
            continue

        cfg = plugin_path / CONFIG_FILE
        if cfg.exists():
            cfg_data = core_utils.structured.import_data_from_json(cfg)
            if cfg_data is None:
                continue

            plugin_data = PluginDescriptor(path=plugin_path, **cfg_data)
            plugins.append(plugin_data)

    return plugins


def discover_plugins() -> list[PluginDescriptor]:
    """
    Scan all directories in CATENA_PLUGIN_PATHS for folders containing
    a plugin.json file.

    Returns:
        list[PluginDescriptor]: List of plugin descriptor objects of valid
            plugins found.
    """
    record = plugin_record.PluginRecordData()
    plugins = discover_client_plugins() + discover_user_plugins()

    for plugin in plugins:
        plugin.enabled = record.is_enabled(plugin.path)

    return plugins
