from dataclasses import dataclass
from dataclasses import field
from pathlib import Path


@dataclass
class PluginDescriptor(object):
    """Small dataclass used to describe a plugin."""

    path: Path
    name: str
    version: str
    author: str
    description: str
    enabled: bool = True
    deferred_load: bool = False
    dependencies: list[str] = field(default_factory=list)
