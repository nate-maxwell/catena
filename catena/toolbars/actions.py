"""
Action functions for the action toolbar buttons.

These are primarily ways to file various nodes or manage the currently
opened file.

Actions are kept here instead of with corresponding shelves in case they ever
need to be invoked independent of the shelves.
"""

import broker

from catena import namespace


class GraphActions(object):

    @classmethod
    def action_save(cls) -> None:
        broker.emit(namespace.FILE_SAVE)

    @classmethod
    def action_undo(cls) -> None:
        broker.emit(namespace.FILE_UNDO)

    @classmethod
    def action_redo(cls) -> None:
        broker.emit(namespace.FILE_REDO)

    @classmethod
    def action_write_files(cls) -> None:
        broker.emit(namespace.NODE_WRITE_FILE)
