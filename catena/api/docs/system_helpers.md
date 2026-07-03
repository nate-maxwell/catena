# System Helpers

The system helpers provide a few application-wide services that plugin code can
use without importing internal modules.

## `api.get_texture_resolution() -> tuple[int, int]`

```python
get_texture_resolution() -> tuple[int, int]
```

Returns the configured texture resolution as a square `(width, height)` pair.

Catena stores texture resolution as a single value in preferences. This helper
converts that setting into the tuple form most texture code expects.

## `api.set_status(status) -> None`

```python
set_status(status: str) -> None
```

Sets the shared status bar text.

This is the public entry point for updating the application status from plugin
code. The change is broadcast through the shared broker event system.

## `api.reset_status() -> None`

```python
reset_status() -> None
```

Restores the default idle status text.

Use this after a plugin action finishes or when temporary status text should be
cleared.

## `api.ShortcutManager`

```python
ShortcutManager
```

Re-exports the shared shortcut manager singleton used across the application.

Use this when a plugin needs to coordinate keyboard shortcuts with the rest of
the UI instead of maintaining a separate shortcut registry.

## Behavior notes

The system helpers are thin wrappers over application state. They are intended
for plugin startup and runtime code that needs to observe or adjust the shared
UI state.
