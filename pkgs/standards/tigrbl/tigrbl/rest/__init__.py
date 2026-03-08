"""Compatibility namespace for legacy REST helpers."""

from __future__ import annotations
from typing import Optional, Type

from .._base import resolve_rest_nested_prefix


def _nested_prefix(model: Type) -> Optional[str]:
    """Compatibility wrapper around ``resolve_rest_nested_prefix``."""

    return resolve_rest_nested_prefix(model)


__all__ = ["_nested_prefix", "resolve_rest_nested_prefix"]
