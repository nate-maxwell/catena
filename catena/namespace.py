"""A list of broker values that are shared across application components."""

# -----Node Events-------------------------------------------------------------
NODE_SELECTED = "node.select.selected"
NODE_PREVIEW = "node.select.preview"
NODE_EVALUATED = "node.evaluated"

NODE_WRITE_FILE = "node.write.write"

GRAPH_OPEN_SUBGRAPH = "graph.subgraph.open"

# -----Model Viewport Events---------------------------------------------------
MODEL_UPDATED_TEXTURE = "model.update.texture"

# -----Client Events-----------------------------------------------------------
FILE_NEW = "client.file.new"
FILE_SAVE = "client.file.save"
FILE_SAVE_AS = "client.file.save_as"
FILE_LOAD = "client.file.load"
FILE_UNDO = "client.file.undo"
FILE_REDO = "client.file.redo"
FILE_CHANGED = "client.file.changed"

STATUS_CHANGED = "client.status.changed"

LOG_ENTRY = "Client.log.message"

PREFERENCES_UPDATED = "prefs.updated"
SESSION_DATA_UPDATED = "session.updated"
PLUGIN_DATA_UPDATED = "plugins.updated"
