from .plugins import (
    registry,
    discover_and_register_plugins,
    PluginManager,
)


def resolve_plugin_spec(group: str, ref: str):
    """Resolve a plugin reference from *group*.

    This compatibility wrapper instantiates a temporary PluginManager and uses
    its internal resolution logic.
    """
    pm = PluginManager({})
    return pm._resolve_spec(group, ref)


__all__ = [
    "registry",
    "discover_and_register_plugins",
    "PluginManager",
    "resolve_plugin_spec",
]
