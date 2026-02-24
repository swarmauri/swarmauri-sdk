"""Utilities for initializing table registries on App and Router facades."""

from __future__ import annotations

import warnings
from typing import Any, Iterable


class RegistryDict(dict[str, Any]):
    """Dict with attribute-style access used by registry containers."""

    def __getattr__(self, name: str) -> Any:
        try:
            value = self[name]
            if isinstance(value, type) and hasattr(value, "__table__"):
                return value.__table__
            return value
        except KeyError as exc:
            raise AttributeError(name) from exc

    def __setattr__(self, name: str, value: Any) -> None:
        self[name] = value


def initialize_table_registry(tables: Iterable[Any]) -> dict[str, Any]:
    """Build the default ``tables`` mapping for an App or Router instance."""

    registry: RegistryDict = RegistryDict()

    for entry in tables or ():
        if isinstance(entry, tuple) and len(entry) == 2 and isinstance(entry[0], str):
            alias, table = entry
            registry[alias] = table
            table_name = getattr(table, "__name__", alias)
            registry.setdefault(table_name, table)
            continue

        table = entry
        table_name = getattr(table, "__name__", None)
        if table_name is None:
            table_name = str(table)
        registry[table_name] = table

    return registry


def initialize_model_registry(models: Iterable[Any]) -> dict[str, Any]:
    """Deprecated alias for :func:`initialize_table_registry`."""

    warnings.warn(
        "initialize_model_registry() is deprecated and will be removed in a "
        "future release; use initialize_table_registry() instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    return initialize_table_registry(models)


__all__ = ["initialize_table_registry", "initialize_model_registry"]
