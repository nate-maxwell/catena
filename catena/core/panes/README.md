# Panes

The core logic for the dockable panes.

`pane.py` contains the baseclass: `DockablePane` and the `PaneConfig` object.

Each pane exists in its own folder until complexity requires it be broken into
multiple files for each of its component parts. They are then moved to a subfolder
for that specific pane.

Utilities exist in `resize` for the client to define layouts.
