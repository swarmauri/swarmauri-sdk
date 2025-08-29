"""General purpose plugin manager supporting domains and groups."""

from importlib import import_module
from importlib.metadata import entry_points
from typing import Any, Dict, Optional, Type

from .registry import PluginDomainRegistry


class PluginManager:
    """Discover, register and load plugins."""

    def __init__(
        self,
        domain: str = "default",
        groups: Optional[Dict[str, tuple[str, type]]] = None,
    ):
        self.domain = domain
        self.groups = groups or {}

    def discover(
        self, mode: str = "fan-out", switch_map: Optional[Dict[str, str]] = None
    ) -> None:
        """Discover entry points and register them in the registry."""
        switch_map = switch_map or {}
        for group_key, (ep_group, base_cls) in self.groups.items():
            eps = list(entry_points(group=ep_group))
            for ep in eps:
                if mode == "switch":
                    target = switch_map.get(group_key)
                    if target and ep.name != target:
                        continue
                obj = ep.load()
                if base_cls and not isinstance(obj, type):
                    raise TypeError(f"Entry-point '{ep.name}' must resolve to a class.")
                if base_cls and not issubclass(obj, base_cls):
                    raise TypeError(
                        f"Entry-point '{ep.name}' in group '{group_key}' must subclass {base_cls.__name__}."
                    )
                PluginDomainRegistry.add(
                    self.domain, group_key, ep.name, f"{ep.module}:{ep.attr}"
                )

    def register(self, group: str, name: str, obj: Type[Any]) -> None:
        """Manually register a plugin class."""
        PluginDomainRegistry.add(
            self.domain, group, name, f"{obj.__module__}:{obj.__name__}"
        )

    def load(self, group: str, name: str, config: str, fmt: str = "json") -> Any:
        """Instantiate a registered plugin using configuration data."""
        path = PluginDomainRegistry.get(self.domain, group, name)
        if not path:
            raise KeyError(f"Plugin '{name}' not registered in group '{group}'.")
        module_path, attr = path.split(":")
        module = import_module(module_path)
        plugin_cls = getattr(module, attr)
        if fmt == "json":
            return plugin_cls.model_validate_json(config)
        if fmt == "yaml":
            return plugin_cls.model_validate_yaml(config)
        if fmt == "toml":
            return plugin_cls.model_validate_toml(config)
        raise ValueError("Unsupported format")

    @staticmethod
    def dump(plugin: Any, fmt: str = "json") -> str:
        """Serialize a plugin instance to JSON, YAML, or TOML."""
        if fmt == "json":
            return plugin.model_dump_json()
        if fmt == "yaml":
            return plugin.model_dump_yaml()
        if fmt == "toml":
            return plugin.model_dump_toml()
        raise ValueError("Unsupported format")
