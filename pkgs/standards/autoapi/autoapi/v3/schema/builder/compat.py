"""Compatibility utilities for schema builder."""

from __future__ import annotations

try:
    # Use SQLAlchemy's hybrid_property when present
    from sqlalchemy.ext.hybrid import hybrid_property  # type: ignore
except Exception:  # pragma: no cover

    class hybrid_property:  # type: ignore
        """Fallback shim when SQLAlchemy is unavailable."""

        pass


try:
    # Pydantic v2 sentinel for "no default"
    from pydantic_core import PydanticUndefined  # type: ignore
except Exception:  # pragma: no cover

    class PydanticUndefinedClass:  # type: ignore
        pass

    PydanticUndefined = PydanticUndefinedClass()  # type: ignore

__all__ = ["hybrid_property", "PydanticUndefined"]
