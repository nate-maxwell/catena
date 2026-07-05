Graph API
=========

This page covers the graph-specific helpers exposed through `catena.api`.
They are the small utility functions plugins can use to interact with the
currently focused graph or open a file in the graph workspace.

## `api.add_to_focussed(node)`

`add_to_focussed` creates a new instance of the given node class and adds it to
the graph that is currently focused in the UI.

Use it when a plugin wants to place a node directly into the graph the user is
working in.

```python
from catena import api


api.add_to_focussed(api.CatenaNode)
```

Behavior:

- looks up the currently focused graph pane
- places the new node at the current view center
- instantiates the node class you pass in

The argument must be a node class, not an instance. The helper calls the class
to create the node before inserting it into the graph.

## `api.open_file(filepath)`

`open_file` opens the file at `filepath` in a new graph tab or view.

Use it when a plugin needs to load a specific file into Catena's graph
workspace.

```python
from pathlib import Path
from catena import api


api.open_file(Path("C:/path/to/image.png"))
```

Behavior:

- accepts a `pathlib.Path` or a value convertible to `Path`
- asks the graph pane to load that filepath
- skips opening it again if the graph is already open
- emits the filepath over `client.file.changed` when the file is opened

This helper is intentionally narrow: it delegates the loading behavior to the
graph pane and does not expose lower-level graph management.
