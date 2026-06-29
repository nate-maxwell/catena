Catena Plugin API
==================

This package exposes the public surface meant for Catena plugins.
Plugin code should import it with:

```python
from catena import api
```

The module re-exports the helpers in this directory, so plugin authors do not
need to import the internal files directly.

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

Example:

```json
{
  "name": "My Plugin",
  "version": "1.0.0",
  "author": "Your Name",
  "description": "Adds a custom node pack and a small utility pane.",
  "deferred_load": false
}
```

If `deferred_load` is `true`, Catena still adds the plugin directory to
`sys.path` immediately, but it postpones running `startup.py` until after the
main plugin queue has finished. Use this when your plugin depends on nodes or
helpers registered by other plugins.

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

Shelf and menu actions
----------------------

Use the toolbar helpers when you want plugin features visible in the main UI.

- `api.add_node_to_shelf(shelf, node_cls, label, icon_path)`
- `api.add_shelf_command(shelf, command, label, icon_path)`
- `api.add_seperator_to_shelf(shelf)`
- `api.add_menu(label)`
- `api.add_toolbar_menu_item(menu, label, command)`

Example:

```python
from catena import api


def install_menu() -> None:
    view_menu = api.add_menu("View")
    api.add_toolbar_menu_item(view_menu, "My Action", lambda: print("hello"))
```

For node buttons, pass a node class to `add_node_to_shelf`. For plain commands,
pass a callable to `add_shelf_command`.

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

System helpers
--------------

The system API exposes a few application-wide helpers:

- `api.get_texture_resolution()` returns the configured square texture size
- `api.set_status(text)` sets the status bar text
- `api.reset_status()` restores the default running status
- `api.ShortcutManager` exposes the shared shortcut manager singleton

Texture helpers
---------------

The texture API is a small wrapper around the image conversion helpers used by
Catena itself. It re-exports:

- `api.ndarray_to_qimage`
- `api.create_texture_from_array`
- `api.bgr_to_rgb`
- `api.rgb_to_bgr`
- `api.bgra_to_rgba`
- `api.rgba_to_bgra`
- `api.TextureType`

These are useful when a plugin generates image data from `numpy` arrays and
needs to hand it to Catena's rendering pipeline.

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
