"""Utilities for initializing registry mappings on App and Router facades."""

from __future__ import annotations

import warnings
from typing import Any, Iterable


class RegistryDict(dict[str, Any]):
    """Dict with attribute-style access used by registry containers."""

    def __getattr__(self, name: str) -> Any:
        try:
            return self[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

    def __setattr__(self, name: str, value: Any) -> None:
        self[name] = value


def initialize_registry(entries: Iterable[Any]) -> RegistryDict:
    """Normalize model/table declarations into a keyed registry.

    Supports bare classes and ``("alias", object)`` tuples. Aliased objects are
    also added under ``__name__`` when available so either lookup style works.
    """

    registry = RegistryDict()

    for entry in entries or ():
        if isinstance(entry, tuple) and len(entry) == 2 and isinstance(entry[0], str):
            alias, obj = entry
            registry[alias] = obj
            obj_name = getattr(obj, "__name__", alias)
            registry.setdefault(obj_name, obj)
            continue

        obj_name = getattr(entry, "__name__", None) or str(entry)
        registry[obj_name] = entry

    return registry


def initialize_table_registry(tables: Iterable[Any]) -> dict[str, Any]:
    """Build the default ``tables`` mapping for an App or Router instance."""

    return initialize_registry(tables)


def initialize_model_registry(models: Iterable[Any]) -> dict[str, Any]:
    """Deprecated alias for :func:`initialize_table_registry`."""

    warnings.warn(
        "initialize_model_registry() is deprecated and will be removed in a "
        "future release; use initialize_table_registry() instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    return initialize_table_registry(models)


__all__ = [
    "RegistryDict",
    "initialize_registry",
    "initialize_table_registry",
    "initialize_model_registry",
]
