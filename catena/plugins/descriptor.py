from dataclasses import dataclass
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
