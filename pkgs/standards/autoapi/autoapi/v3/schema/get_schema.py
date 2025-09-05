from __future__ import annotations

from typing import Literal, Optional, Type

from pydantic import BaseModel


def get_schema(
    orm_cls: type,
    op: str,
    *,
    kind: Literal["in", "out"] = "out",
) -> Optional[Type[BaseModel]]:
    """Return the bound schema for ``orm_cls``.

    Parameters
    ----------
    orm_cls:
        ORM model that has been bound via :func:`autoapi.v3.bindings.build_schemas`.
    op:
        Operation alias whose schema should be returned.
    kind:
        Either ``"in"`` for request schemas or ``"out"`` for response schemas.

    Returns
    -------
    Optional[Type[BaseModel]]
        The requested schema class if available, otherwise ``None`` when the
        operation uses raw payloads.

    Raises
    ------
    KeyError
        If the model has not been bound or the operation/kind is unknown.
    """
    ns = getattr(orm_cls, "schemas", None)
    if ns is None:
        raise KeyError(
            f"{orm_cls.__name__} has no bound schemas; did you include the model?",
        )

    alias_ns = getattr(ns, op, None)
    if alias_ns is None:
        raise KeyError(f"Unknown op '{op}' for {orm_cls.__name__}")

    kind = kind.lower()
    if kind not in {"in", "out"}:
        raise ValueError("kind must be 'in' or 'out'")

    attr = "in_" if kind == "in" else "out"
    if not hasattr(alias_ns, attr):
        raise KeyError(
            f"Schema kind '{kind}' not found for op '{op}' on {orm_cls.__name__}",
        )
    return getattr(alias_ns, attr)


__all__ = ["get_schema"]
