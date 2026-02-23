"""Route-focused decorators that build on ``op_ctx`` / ``OpSpec`` metadata."""

from __future__ import annotations

from dataclasses import replace
from typing import Iterable, Optional, Sequence

from ..op.decorators import _unwrap, op_ctx
from ..op.types import Arity, PersistPolicy, TargetOp
from ..schema.types import SchemaArg


def _normalize_methods(methods: Sequence[str] | str | None) -> tuple[str, ...] | None:
    if methods is None:
        return None
    if isinstance(methods, str):
        values = [methods]
    else:
        values = list(methods)
    normalized = tuple(m.upper() for m in values if str(m).strip())
    return normalized or None


def _normalize_path(path: str | None) -> str | None:
    if path is None:
        return None
    p = path.strip()
    if not p or p == "/":
        return ""
    return p if p.startswith("/") else f"/{p}"


def route_ctx(
    path: str | None = None,
    *,
    methods: Sequence[str] | str | None = None,
    bind: object | Iterable[object] | None = None,
    alias: Optional[str] = None,
    target: Optional[TargetOp] = "custom",
    arity: Optional[Arity] = None,
    rest: Optional[bool] = True,
    request_schema: Optional[SchemaArg] = None,
    response_schema: Optional[SchemaArg] = None,
    persist: Optional[PersistPolicy] = None,
    status_code: Optional[int] = None,
    tags: Sequence[str] | None = None,
):
    """Declare a ctx operation with explicit route metadata.

    This decorator composes :func:`op_ctx` and then enriches the underlying
    ``__tigrbl_op_spec__`` payload so ``mro_collect_decorated_ops`` can build a
    corresponding :class:`~tigrbl.op.OpSpec` that carries route hints
    (``path_suffix``, ``http_methods``, and optional ``tags``).
    """

    normalized_methods = _normalize_methods(methods)
    path_suffix = _normalize_path(path)
    normalized_tags = tuple(tags or ())

    def deco(fn):
        decorated = op_ctx(
            bind=bind,
            alias=alias,
            target=target,
            arity=arity,
            rest=rest,
            request_schema=request_schema,
            response_schema=response_schema,
            persist=persist,
            status_code=status_code,
        )(fn)

        base_fn = _unwrap(decorated)
        op_spec = getattr(base_fn, "__tigrbl_op_spec__", None)
        if op_spec is None:
            op_spec = getattr(base_fn, "__tigrbl_op_decl__", None)
        if op_spec is None:
            return decorated

        if normalized_methods is not None:
            op_spec = replace(op_spec, http_methods=normalized_methods)
        if path_suffix is not None:
            op_spec = replace(op_spec, path_suffix=path_suffix)
        if normalized_tags:
            op_spec = replace(op_spec, tags=normalized_tags)

        base_fn.__tigrbl_op_spec__ = op_spec
        base_fn.__tigrbl_op_decl__ = op_spec
        return decorated

    return deco


__all__ = ["route_ctx"]
