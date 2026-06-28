from __future__ import annotations

from typing import TYPE_CHECKING

from catena.panes.pane import DockablePane
from catena.panes.pane import PaneConfig

if TYPE_CHECKING:
    from catena.client import CatenaEditor

__all__ = [
    "DockablePane",
    "PaneConfig",
    "get_reference_to_base_client",
]


_client_ref: CatenaEditor | None = None


def init_client_ref(client_ref: CatenaEditor | None = None) -> None:
    global _client_ref
    if client_ref is None:
        return

    _client_ref = client_ref


def get_reference_to_base_client() -> CatenaEditor:
    global _client_ref
    if _client_ref is None:
        raise RuntimeError(
            "Base client reference was never populated."
            "Startup procedure executed invalidly."
        )

    return _client_ref
