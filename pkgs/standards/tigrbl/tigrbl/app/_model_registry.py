"""Utilities for initializing model registries on App and API facades."""

from __future__ import annotations

from typing import Any, Iterable


def initialize_model_registry(models: Iterable[Any]) -> dict[str, Any]:
    """Build the default ``models`` mapping for an App or Api instance.

    ``defineAppSpec``/``defineApiSpec`` allow authors to declare default models
    using bare model classes or ``("alias", Model)`` tuples.  Runtime facades,
    however, expect ``self.models`` to be a dictionary keyed by model name so
    that lookups like ``app.models["Widget"]`` Just Work.

    This helper normalizes the declared sequence into that dictionary shape and
    preserves declaration order.  When an alias is provided we register both the
    alias and the model's ``__name__`` so either lookup style succeeds.
    """

    registry: dict[str, Any] = {}

    for entry in models or ():
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


__all__ = ["initialize_model_registry"]
