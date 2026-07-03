Catena Plugin API
==================

This package exposes the public surface meant for Catena plugins.
Plugin code should import it with:

```python
from catena import api
```

The module contains safe interfaces for plugin authors to leverage without
needing extensive knowledge of Catena's internals.

Plugin layout
-------------

Catena discovers plugins by scanning folders that contain a `plugin.json`
manifest. Built-in plugins are loaded from the bundled `plugins/` directory.
User plugins are loaded from the paths listed in the `CATENA_PLUGIN_PATHS`
environment variable.

Each plugin folder should contain:

```text
my_plugin/
  plugin.json
  startup.py
  my_files.py
```

`startup.py` is the entrypoint Catena runs when the plugin is enabled. The
plugin folder is added to `sys.path` before startup runs, so local modules can be
imported normally.

`plugin.json`
-------------

The manifest is a small JSON object with these fields:

- `name`: display name for the plugin
- `version`: plugin version string
- `author`: author name(s)
- `description`: short summary shown in the plugin manager
- `deferred_load`: optional boolean that delays `startup.py` until all other
  non-deferred plugins have been initialized
- `dependencies`: optional list of plugin names or folder names that must be
  available before this plugin will load

Example:

```json
{
  "name": "My Plugin",
  "version": "1.0.0",
  "author": "Your Name",
  "description": "Adds a custom node pack and a small utility pane.",
  "deferred_load": false,
  "dependencies": ["standard_node_library"]
}
```

If `deferred_load` is `true`, Catena still adds the plugin directory to
`sys.path` immediately, but it postpones running `startup.py` until after the
main plugin queue has finished. Use this when your plugin depends on nodes or
helpers registered by other plugins.

If any dependency is missing, disabled, or fails to load, Catena skips the
plugin instead of running its startup code.

What plugins usually do
-----------------------

Most plugins do one or more of the following:

1. register custom node classes
2. add node buttons to a shelf
3. add menu items
4. create a dockable pane
5. update the status bar

The API is grouped around those tasks.

Node registration
-----------------

Use `api.register_node(category, node_cls)` to make a node available to the
graph system.

```python
from catena import api

CATEGORY = "My Nodes"


class MyNode(api.CatenaNode):
    def __init__(self) -> None:
        super().__init__("My Node")


api.register_node(CATEGORY, MyNode)
```

The node API also re-exports the core building blocks used by node classes:

- `api.CatenaNode`
- `api.Port`
- `api.PortType`
- `api.PortDataType`
- `api.FieldDefinition`
- `api.FieldType`
- `api.DATA_TYPE_COLORS`
- `api.FIELD_PORT_DATA_TYPES`
- `api.TEXTURE_DATA_TYPES`

You can read more about custom node construction [here](docs/nodes.md).

Preferences
-----------

Plugins can register their own dataclass-backed settings objects with the shared
preferences singleton:

```python
from dataclasses import dataclass
from catena import api


@dataclass
class MyPluginPreferences:
    enabled: bool = True
    intensity: float = 1.0


prefs = api.register_preferences("my_plugin_preferences", MyPluginPreferences)
prefs.enabled = False
api.save_preferences()
```

Use `api.register_preferences`, `api.get_preferences`, `api.list_preferences`,
and `api.save_preferences` to manage plugin-specific settings.

Click [here](docs/preferences.md) to learn more.

Shelf and menu actions
----------------------

Use the toolbar helpers to add shelf buttons, menu actions, and shared status
updates from plugin code.

Click [here](docs/shelf_and_menu_actions.md) to learn more.

Dockable panes
--------------

Plugins can create dockable panes by subclassing `api.DockablePane`. The base
class handles docking, layout wiring, and visibility controls.

```python
from PySide6TK import QtCore
from PySide6 import QtWidgets
from catena import api


class MyPane(api.DockablePane):
    pane_config = api.PaneConfig(
        title="My Pane",
        default_area=QtCore.Qt.DockWidgetArea.RightDockWidgetArea,
    )

    def create_widgets(self) -> None:
        self.label = QtWidgets.QLabel("Hello", self.content_widget)

    def create_layouts(self) -> None:
        self.content_layout.addWidget(self.label)

    def create_connections(self) -> None:
        pass
```

If a pane needs access to the main window, call
`api.get_reference_to_base_client()` from `startup.py` and pass the reference
into your pane constructor.

Click [here](docs/dockable_panes.md) to learn more.

System helpers
--------------

The system API exposes shared helpers for texture resolution, status updates,
and shortcuts.

Click [here](docs/system_helpers.md) to learn more.

Texture helpers
---------------

The texture API re-exports the image conversion helpers used by Catena's
rendering pipeline.

Click [here](docs/texture_helpers.md) to learn more.

Application stack
-----------------

Catena is built on `numpy`, `opencv-python`/`cv2`, `scipy`, `PySide6`, and the
shared `broker` event system.

Click [here](docs/application_stack.md) to learn more.

Startup pattern
---------------

Most plugins follow this shape:

```python
from catena import api
from .my_node import MyNode

CATEGORY = "My Plugin"


def initialize() -> None:
    api.register_node(CATEGORY, MyNode)


initialize()
```

If your plugin adds toolbar entries or panes, build them in `startup.py` after
the relevant classes have been imported. Keep startup side effects small and
deterministic so plugin loading stays predictable.

Notes
-----

- Catena enables discovered plugins by default and only persists disabled paths.
- The plugin manager stores that state in the user's app data directory.
- A plugin folder must exist and contain a valid `plugin.json` to be discovered.
