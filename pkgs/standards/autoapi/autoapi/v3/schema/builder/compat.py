"""Compatibility utilities for schema builder."""

from __future__ import annotations

try:
    # Pydantic v2 sentinel for "no default"
    from pydantic_core import PydanticUndefined  # type: ignore
except Exception:  # pragma: no cover

    class PydanticUndefinedClass:  # type: ignore
        pass

    PydanticUndefined = PydanticUndefinedClass()  # type: ignore


__all__ = ["PydanticUndefined"]
