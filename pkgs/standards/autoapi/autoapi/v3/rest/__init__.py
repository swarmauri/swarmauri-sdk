"""autoapi_routes.py
Helpers that build path prefixes for nested REST endpoints.
The logic is intentionally minimal; extend or override as needed.
"""

from __future__ import annotations
from typing import Type, Optional
from ..config.constants import NESTED_PATHS_ATTR


def _nested_prefix(self, model: Type) -> Optional[str]:
    """Return the user-supplied hierarchical prefix or *None*.

    • If the SQLAlchemy model defines `__autoapi_nested_paths__`
      → call it and return the result.
    • Else, fall back to legacy `_nested_path` string if present.
    • Otherwise → signal ``no nested route wanted`` with ``None``.
    """

    cb = getattr(model, NESTED_PATHS_ATTR, None)
    if callable(cb):
        return cb()
    return getattr(model, "_nested_path", None)


__all__ = ["_nested_prefix"]
