"""tigrbl_routes.py
Helpers that build path prefixes for nested REST endpoints.
The logic is intentionally minimal; extend or override as needed.
"""

from __future__ import annotations
from typing import Optional, Type

from .._spec.binding_spec import resolve_rest_nested_prefix


def _nested_prefix(model: Type) -> Optional[str]:
    """Compatibility wrapper around ``resolve_rest_nested_prefix``."""

    return resolve_rest_nested_prefix(model)


__all__ = ["_nested_prefix", "resolve_rest_nested_prefix"]
