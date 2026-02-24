"""Utilities for initializing model registries on App and Router facades."""

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


def initialize_table_registry(tables: Iterable[Any]) -> dict[str, Any]:
    """Build the default ``tables`` mapping for an App or Router instance.

    ``defineAppSpec``/``defineRouterSpec`` allow authors to declare default models
    using bare model classes or ``("alias", Model)`` tuples. Runtime facades,
    however, expect ``self.tables`` to be a dictionary keyed by model name so
    that lookups like ``app.tables["Widget"]`` just work.

    This helper normalizes the declared sequence into that dictionary shape and
    preserves declaration order. When an alias is provided we register both the
    alias and the model's ``__name__`` so either lookup style succeeds.
    """

    registry: RegistryDict = RegistryDict()

    for entry in tables or ():
        # Support ``("Alias", Model)`` declarations in addition to bare models.
        if isinstance(entry, tuple) and len(entry) == 2 and isinstance(entry[0], str):
            alias, model = entry
            registry[alias] = model
            model_name = getattr(model, "__name__", alias)
            registry.setdefault(model_name, model)
            continue

        model = entry
        model_name = getattr(model, "__name__", None)
        if model_name is None:
            model_name = str(model)
        registry[model_name] = model

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
