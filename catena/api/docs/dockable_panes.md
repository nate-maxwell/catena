# Dockable Panes

Catena exposes dockable panes through `catena.api` so plugins can build
tooling that attaches to the main window without depending on internal pane
implementation details.

## `api.PaneConfig`

```python
PaneConfig(
    title: str = "Pane",
    default_area: QtCore.Qt.DockWidgetArea = QtCore.Qt.DockWidgetArea.LeftDockWidgetArea,
    allowed_areas: QtCore.Qt.DockWidgetArea = (
        QtCore.Qt.DockWidgetArea.LeftDockWidgetArea
        | QtCore.Qt.DockWidgetArea.RightDockWidgetArea
        | QtCore.Qt.DockWidgetArea.TopDockWidgetArea
        | QtCore.Qt.DockWidgetArea.BottomDockWidgetArea
    ),
    features: QtWidgets.QDockWidget.DockWidgetFeature = (
        QtWidgets.QDockWidget.DockWidgetFeature.DockWidgetMovable
        | QtWidgets.QDockWidget.DockWidgetFeature.DockWidgetFloatable
        | QtWidgets.QDockWidget.DockWidgetFeature.DockWidgetClosable
    ),
    starts_floating: bool = False,
    min_size: tuple[int, int] = (200, 150),
)
```

Configuration object for pane placement and behavior.

Use it to control the pane title, default dock area, allowed docking areas,
Qt dock widget flags, floating state, and minimum size.

## `api.DockablePane`

```python
DockablePane(main_window: QtWidgets.QMainWindow, config: PaneConfig | None = None)
```

Base class for dockable panes.

Subclass it and implement `create_widgets`, `create_layouts`, and
`create_connections` to build the pane's content. Child widgets should be
parented to `self.content_widget`.

The base class:

- creates the internal content widget and vertical layout
- applies the configured dock area and window features
- calls the subclass hooks in order
- adds the pane to the supplied main window
- supports floating panes when requested by configuration

### Subclass hooks

```python
create_widgets(self) -> None
create_layouts(self) -> None
create_connections(self) -> None
```

Override these in derived classes to build the UI, arrange widgets, and connect
signals.

### Convenience methods

```python
toggle_visibility(self) -> None
raise_pane(self) -> None
```

`toggle_visibility` switches the pane between visible and hidden.
`raise_pane` brings the pane to the front when it is tabbed with other panes.

## `api.get_reference_to_base_client() -> CatenaEditor`

```python
get_reference_to_base_client() -> CatenaEditor
```

Returns the main Catena client window reference.

Call this from plugin startup code when a pane or other UI object needs access
to the main window after initialization. The reference is injected by the
client at startup.

## Behavior notes

Pane construction is intentionally explicit: the plugin supplies the main
window, Catena constructs the dock widget, and the subclass fills in the
content. That keeps the pane API predictable and easy to compose with the rest
of the UI.
