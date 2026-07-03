# Application Stack

Catena is built on `numpy`, `opencv-python`/`cv2`, `scipy`, `PySide6`, and the
`broker` event system that lives in the virtual environment.

## `numpy`

Catena uses `numpy` for array-based image data and node outputs.

Most texture and node-processing code works with numeric arrays first, then
converts those arrays into Qt or Catena texture objects when needed.

## `opencv-python` / `cv2`

Catena uses OpenCV for image-processing operations that are awkward or slow to
build by hand.

The texture helpers and node code rely on OpenCV's array-oriented image
manipulation model, especially where channel conversions and image transforms
are involved.

## `scipy`

Catena uses SciPy for numerical operations that go beyond basic array handling.

This fits the application's procedural texture workflow, where filters and
math-heavy processing are part of normal node evaluation.

## `PySide6`

Catena uses PySide6 for the desktop UI.

Windows, menus, toolbars, panes, dialogs, and widgets are built on Qt through
this binding.

## `broker`

Catena uses `broker` as its shared event bus.

The package is imported directly as `import broker` and acts as a module facade
for the runtime broker instance. Catena relies on broker events to decouple
application areas such as preferences, status updates, graph changes, and
toolbar actions.

Common broker operations in Catena include:

- `broker.emit(...)` for synchronous event delivery
- `broker.register_subscriber(...)` for listening to application events
- `broker.register_transformer(...)` for intercepting or modifying event data
- `broker.stage(...)` and the staged emit helpers for deferred delivery

## Architecture note

The overall design is array-first for image processing, Qt-based for the user
interface, and broker-driven for cross-component communication. That keeps the
editor responsive while avoiding direct coupling between unrelated systems.
