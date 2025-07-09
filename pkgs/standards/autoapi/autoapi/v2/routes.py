"""autoapi_routes.py
Helpers that build path prefixes for nested REST endpoints.
The logic is intentionally minimal; extend or override as needed.
"""

from __future__ import annotations
from typing import Type, Optional


def _nested_prefix(self, model: Type) -> Optional[str]:
    """Return the user-supplied hierarchical prefix or *None*.

    • If the SQLAlchemy model defines a `_nested_path` string
      → return it verbatim.
    • Otherwise → signal ``no nested route wanted`` with ``None``.
    """

    return getattr(model, "_nested_path", None)
