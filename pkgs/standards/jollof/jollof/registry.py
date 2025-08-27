"""Generic registry for plugin domains and groups."""

from collections import defaultdict
from typing import Dict


class PluginDomainRegistry:
    """Maintain plugin registrations keyed by domain and group."""

    _registry: Dict[str, Dict[str, Dict[str, str]]] = defaultdict(
        lambda: defaultdict(dict)
    )

    @classmethod
    def add(cls, domain: str, group: str, name: str, object_path: str) -> None:
        """Register a plugin under a domain and group."""
        cls._registry[domain][group][name] = object_path

    @classmethod
    def get(cls, domain: str, group: str, name: str) -> str | None:
        """Retrieve a registered plugin path."""
        return cls._registry.get(domain, {}).get(group, {}).get(name)

    @classmethod
    def remove(cls, domain: str, group: str, name: str) -> None:
        cls._registry.get(domain, {}).get(group, {}).pop(name, None)

    @classmethod
    def update(cls, domain: str, group: str, name: str, object_path: str) -> None:
        cls._registry[domain][group][name] = object_path

    @classmethod
    def delete_group(cls, domain: str, group: str) -> None:
        cls._registry.get(domain, {}).pop(group, None)

    @classmethod
    def known_domains(cls) -> list[str]:
        return list(cls._registry.keys())

    @classmethod
    def known_groups(cls, domain: str) -> list[str]:
        return list(cls._registry.get(domain, {}).keys())

    @classmethod
    def total_registry(cls) -> Dict[str, Dict[str, Dict[str, str]]]:
        return cls._registry
