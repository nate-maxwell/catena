# Shelf and Menu Actions

These helpers connect plugins to the main editor UI. They let plugin code add
buttons to shelves, attach commands to menus, and update the shared status
display.

## `api.add_node_to_shelf(shelf, node, label, icon_path=Resources.BUTTON_WHITE_40X40) -> None`

```python
add_node_to_shelf(
    shelf: str,
    node: type[CatenaNode],
    label: str,
    icon_path: Path = Resources.BUTTON_WHITE_40X40,
) -> None
```

Adds a node-spawning button to the named shelf.

Use this when the toolbar action should instantiate a node class in the graph
editor. The shelf is created if it does not already exist.

## `api.add_shelf_command(shelf, command, label, icon_path=Resources.BUTTON_WHITE_40X40) -> None`

```python
add_shelf_command(
    shelf: str,
    command: Callable,
    label: str,
    icon_path: Path = Resources.BUTTON_WHITE_40X40,
) -> None
```

Adds a callable command to the named shelf.

Use this when the button should run arbitrary plugin code instead of spawning a
node.

## `api.add_seperator_to_shelf(shelf) -> None`

```python
add_seperator_to_shelf(shelf: str) -> None
```

Adds a spacing separator to the named shelf.

This is useful for grouping related shelf buttons.

## `api.add_menu(label) -> QtWidgets.QMenu`

```python
add_menu(label: str) -> QtWidgets.QMenu
```

Creates or retrieves a menu on the shared menu toolbar.

The returned `QMenu` can be reused as the parent menu for additional menu
items.

## `api.add_toolbar_menu_item(submenu, cmd_name, cmd=null) -> None`

```python
add_toolbar_menu_item(
    submenu: QtWidgets.QMenu, cmd_name: str, cmd: Callable = null
) -> None
```

Adds a callable command to an existing menu.

If no command is supplied, Catena uses a no-op placeholder, so the menu entry
still exists even when the plugin is wiring it up in stages.

## `api.set_status(status) -> None`

```python
set_status(status: str) -> None
```

Sets the shared status bar text.

This emits the broker status change event used by the application UI.

## `api.reset_status() -> None`

```python
reset_status() -> None
```

Restores the default idle status text.

Use this after a plugin action finishes or when temporary status text should be
cleared.

## Behavior notes

These helpers depend on the client having initialized the shared toolbar
references. They are intended for plugin startup code after the main window has
been constructed.
