# Preferences API

Catena stores settings in a shared preferences singleton. The public API in
`catena.api` exposes a small wrapper around that singleton so plugins can
register and retrieve their own settings objects without depending on internal
modules.

## `api.register_preferences(key, settings_cls) -> T`

```python
register_preferences(key: str, settings_cls: type[T]) -> T
```

Registers a dataclass-backed settings object under a persistent key and returns
the live instance stored by Catena.

Use this when a plugin needs its own settings section. The returned object is
the one Catena keeps in memory, so edits are applied directly to the active
preferences state.

## `api.get_preferences(key) -> Any`

```python
get_preferences(key: str) -> Any
```

Returns a previously registered settings object.

Call this when you need to look up a settings section later by key.

## `api.list_preferences() -> tuple[str, ...]`

```python
list_preferences() -> tuple[str, ...]
```

Returns the currently registered preference keys.

This is useful for inspection, debugging, or tooling that needs to know which
sections are currently active.

## `api.save_preferences() -> None`

```python
save_preferences() -> None
```

Writes the current preferences snapshot to disk.

Saving preferences also emits the `prefs.updated` broker event, so other
systems can react to preference changes without holding a direct reference to
the preferences object.

## Behavior notes

`register_preferences` expects `settings_cls` to be a dataclass type. The
stored object is persistent and is recreated from disk if saved data already
exists for the given key.

Unknown sections loaded from disk are preserved, which allows settings from a
missing or disabled plugin to remain in the user's file.
