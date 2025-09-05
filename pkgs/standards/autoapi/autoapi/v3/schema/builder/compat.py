"""Compatibility utilities for schema builder."""

from __future__ import annotations

from typing import Any, Mapping

try:
    # Optional: validate column metadata if available
    from ...info_schema import check as _info_check  # type: ignore
except Exception:  # pragma: no cover

    def _info_check(meta: Mapping[str, Any], attr_name: str, model_name: str) -> None:
        return None


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


__all__ = ["_info_check", "hybrid_property", "PydanticUndefined"]
