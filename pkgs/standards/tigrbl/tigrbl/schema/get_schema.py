from __future__ import annotations

import logging
from typing import Literal, Optional, Type

from pydantic import BaseModel

logger = logging.getLogger("uvicorn")


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
        ORM model that has been bound via :func:`tigrbl.bindings.build_schemas`.
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
    logger.debug(
        "Resolving schema for model=%s op=%s kind=%s", orm_cls.__name__, op, kind
    )

    ns = getattr(orm_cls, "schemas", None)
    if ns is None:
        logger.debug("Model %s has no schemas namespace", orm_cls.__name__)
        raise KeyError(
            f"{orm_cls.__name__} has no bound schemas; did you include the model?",
        )
    logger.debug("Found schemas namespace for model %s", orm_cls.__name__)

    alias_ns = getattr(ns, op, None)
    if alias_ns is None:
        logger.debug("Unknown operation '%s' for model %s", op, orm_cls.__name__)
        raise KeyError(f"Unknown op '{op}' for {orm_cls.__name__}")
    logger.debug("Found operation '%s' for model %s", op, orm_cls.__name__)

    kind = kind.lower()
    if kind not in {"in", "out"}:
        logger.debug("Invalid schema kind '%s' requested", kind)
        raise ValueError("kind must be 'in' or 'out'")
    logger.debug("Using schema kind '%s'", kind)

    attr = "in_" if kind == "in" else "out"
    if not hasattr(alias_ns, attr):
        logger.debug(
            "Schema kind '%s' not found for op '%s' on %s", kind, op, orm_cls.__name__
        )
        raise KeyError(
            f"Schema kind '{kind}' not found for op '{op}' on {orm_cls.__name__}",
        )
    logger.debug(
        "Found schema attribute '%s' for op '%s' on %s", attr, op, orm_cls.__name__
    )
    schema = getattr(alias_ns, attr)
    logger.debug(
        "Resolved schema %s for model %s op=%s kind=%s",
        schema,
        orm_cls.__name__,
        op,
        kind,
    )
    return schema


__all__ = ["get_schema"]
