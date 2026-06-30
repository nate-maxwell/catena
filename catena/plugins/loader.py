"""
Loads enabled plugins on startup by extending sys.path and running
any startup.py files found in enabled plugin folders.
"""

import heapq
import importlib.util
import logging
import sys
from pathlib import Path

from catena.plugins.descriptor import PluginDescriptor
from catena.plugins.discover import discover_plugins

logger = logging.getLogger(__name__)


def _plugin_id(descriptor: PluginDescriptor) -> str:
    """Return the stable identifier used for dependency tracking."""
    return descriptor.path.as_posix()


def _matches_dependency_reference(
    descriptor: PluginDescriptor, reference: str
) -> bool:
    """Return True when a dependency reference points at a plugin."""
    return reference in {
        descriptor.name,
        descriptor.path.name,
        descriptor.path.as_posix(),
        str(descriptor.path),
    }


def _resolve_dependency_reference(
    reference: str, plugins: list[PluginDescriptor]
) -> PluginDescriptor | None:
    """
    Resolve a dependency reference to exactly one discovered plugin.

    References may match either the plugin's declared name or its folder name.
    """
    matches = [
        descriptor
        for descriptor in plugins
        if _matches_dependency_reference(descriptor, reference)
    ]

    if len(matches) == 1:
        return matches[0]

    return None


def _run_startup(plugin_path: Path) -> bool:
    """Run a startup.py file if it can be found in the given plugin path."""
    startup = plugin_path / "startup.py"
    if not startup.exists():
        return True

    try:
        spec = importlib.util.spec_from_file_location(
            f"{plugin_path.name}.startup", startup
        )
        if spec is None or spec.loader is None:
            raise ImportError(f"Could not load startup module from {startup}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        logger.info(f"Ran startup.py for plugin: {plugin_path.name}")
        return True
    except Exception as e:
        logger.exception(f"Failed to run startup.py for plugin {plugin_path.name}: {e}")
        return False


def _extend_path_to_plugin(plugin_path: Path) -> None:
    """
    Extend the sys path to the given plugin path if it hasn't been extended
    already.
    """
    path_str = str(plugin_path)
    if path_str not in sys.path and plugin_path.as_posix() not in sys.path:
        sys.path.insert(0, path_str)
        logger.info(f"Extended sys.path with {plugin_path.name}")


def _build_dependency_graph(
    plugins: list[PluginDescriptor],
) -> tuple[dict[str, list[str]], dict[str, list[str]]]:
    """
    Build the dependency graph for the supplied plugins.

    Returns:
        A tuple of:
        - resolved dependency ids keyed by plugin id
        - unresolved dependency references keyed by plugin id
    """
    resolved_dependencies: dict[str, list[str]] = {}
    unresolved_dependencies: dict[str, list[str]] = {}

    for plugin in plugins:
        plugin_id = _plugin_id(plugin)
        resolved_dependencies[plugin_id] = []
        unresolved_dependencies[plugin_id] = []

        for reference in plugin.dependencies:
            resolved = _resolve_dependency_reference(reference, plugins)

            if resolved is None:
                unresolved_dependencies[plugin_id].append(reference)
                logger.warning(
                    "Skipping plugin %s because dependency %r could not be resolved.",
                    plugin.name,
                    reference,
                )
                continue

            if resolved is plugin:
                unresolved_dependencies[plugin_id].append(reference)
                logger.warning(
                    "Skipping plugin %s because it depends on itself.",
                    plugin.name,
                )
                continue

            resolved_dependencies[plugin_id].append(_plugin_id(resolved))

    return resolved_dependencies, unresolved_dependencies


def _prune_blocked_plugins(
    resolved_dependencies: dict[str, list[str]],
    unresolved_dependencies: dict[str, list[str]],
) -> set[str]:
    """
    Return the set of plugin ids that cannot be loaded.

    Any plugin with an unresolved dependency is blocked, and that blockage
    propagates to any plugin that depends on it.
    """
    blocked = {plugin_id for plugin_id, refs in unresolved_dependencies.items() if refs}
    changed = True

    while changed:
        changed = False
        for plugin_id, deps in resolved_dependencies.items():
            if plugin_id in blocked:
                continue

            if any(dependency_id in blocked for dependency_id in deps):
                blocked.add(plugin_id)
                changed = True

    return blocked


def _order_plugins(
    plugins: list[PluginDescriptor],
    resolved_dependencies: dict[str, list[str]],
) -> list[PluginDescriptor]:
    """
    Topologically order plugins so dependencies run before dependents.

    When multiple plugins are available at once, non-deferred plugins load first.
    """
    plugin_lookup = {_plugin_id(plugin): plugin for plugin in plugins}
    adjacency: dict[str, list[str]] = {plugin_id: [] for plugin_id in plugin_lookup}
    indegree: dict[str, int] = {plugin_id: 0 for plugin_id in plugin_lookup}

    for plugin_id, dependencies in resolved_dependencies.items():
        if plugin_id not in plugin_lookup:
            continue

        for dependency_id in dependencies:
            if dependency_id not in plugin_lookup:
                continue

            adjacency[dependency_id].append(plugin_id)
            indegree[plugin_id] += 1

    heap: list[tuple[tuple[int, str, str], str]] = []
    for plugin_id, degree in indegree.items():
        if degree == 0:
            descriptor = plugin_lookup[plugin_id]
            priority = (
                1 if descriptor.deferred_load else 0,
                descriptor.name.lower(),
                descriptor.path.as_posix(),
            )
            heapq.heappush(heap, (priority, plugin_id))

    ordered_ids: list[str] = []
    while heap:
        _, plugin_id = heapq.heappop(heap)
        ordered_ids.append(plugin_id)

        for dependent_id in adjacency[plugin_id]:
            indegree[dependent_id] -= 1
            if indegree[dependent_id] == 0:
                descriptor = plugin_lookup[dependent_id]
                priority = (
                    1 if descriptor.deferred_load else 0,
                    descriptor.name.lower(),
                    descriptor.path.as_posix(),
                )
                heapq.heappush(heap, (priority, dependent_id))

    if len(ordered_ids) != len(plugin_lookup):
        unresolved = sorted(
            set(plugin_lookup) - set(ordered_ids),
            key=lambda plugin_id: plugin_lookup[plugin_id].path.as_posix(),
        )
        for plugin_id in unresolved:
            logger.warning(
                "Skipping plugin %s because its dependencies could not be ordered.",
                plugin_lookup[plugin_id].name,
            )

    return [plugin_lookup[plugin_id] for plugin_id in ordered_ids]


def load_plugins() -> None:
    """
    For each enabled plugin:
    - Add the plugin folder to sys.path so it can be imported as a library
    - Run startup.py if present
    """
    discovered_plugins = [plugin for plugin in discover_plugins() if plugin.enabled]
    resolved_dependencies, unresolved_dependencies = _build_dependency_graph(
        discovered_plugins
    )
    blocked_plugins = _prune_blocked_plugins(
        resolved_dependencies, unresolved_dependencies
    )

    loadable_plugins = [
        plugin
        for plugin in discovered_plugins
        if _plugin_id(plugin) not in blocked_plugins
    ]
    ordered_plugins = _order_plugins(loadable_plugins, resolved_dependencies)

    for descriptor in ordered_plugins:
        _extend_path_to_plugin(descriptor.path)

    loaded_plugins: set[str] = set()
    for descriptor in ordered_plugins:
        plugin_id = _plugin_id(descriptor)
        dependency_ids = resolved_dependencies.get(plugin_id, [])

        if any(dependency_id not in loaded_plugins for dependency_id in dependency_ids):
            logger.warning(
                "Skipping plugin %s because one or more dependencies failed to load.",
                descriptor.name,
            )
            continue

        if _run_startup(descriptor.path):
            loaded_plugins.add(plugin_id)
