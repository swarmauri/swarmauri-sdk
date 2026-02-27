"""Utilities for initializing model registries on App and Router facades."""

from __future__ import annotations

import warnings
from typing import Any, Iterable

from .._concrete._table_registry import TableRegistry


RegistryDict = TableRegistry


def initialize_table_registry(tables: Iterable[Any]) -> TableRegistry:
    """Build the default ``tables`` mapping for an App or Router instance.

    ``defineAppSpec``/``defineRouterSpec`` allow authors to declare default models
    using bare model classes or ``("alias", Model)`` tuples. Runtime facades,
    however, expect ``self.tables`` to be a dictionary keyed by model name so
    that lookups like ``app.tables["Widget"]`` just work.

    This helper normalizes the declared sequence into that dictionary shape and
    preserves declaration order. When an alias is provided we register both the
    alias and the model's ``__name__`` so either lookup style succeeds.
    """

    return TableRegistry(tables=tables)


def initialize_model_registry(models: Iterable[Any]) -> TableRegistry:
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
    "initialize_table_registry",
    "initialize_model_registry",
]
