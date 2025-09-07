# autoapi/v3/ops/collect.py
from __future__ import annotations

import logging
from typing import Any, Callable, Dict

from .types import OpSpec
from .decorators import _maybe_await, _OpDecl, _infer_arity, _normalize_persist, _unwrap
from ..runtime.executor import _Ctx

logger = logging.getLogger("uvicorn")


def _merge_mro_dict(cls: type, attr: str) -> Dict[str, Any]:
    merged: Dict[str, Any] = {}
    for base in reversed(cls.__mro__):
        merged.update(getattr(base, attr, {}) or {})
    return merged


def alias_map_for(table: type) -> Dict[str, str]:
    """Merge aliases across MRO; subclass wins."""
    return _merge_mro_dict(table, "__autoapi_aliases__")


def apply_alias(verb: str, alias_map: Dict[str, str]) -> str:
    """Resolve canonical verb → alias (falls back to verb)."""
    return alias_map.get(verb, verb)


def _wrap_ctx_core(table: type, func: Callable[..., Any]) -> Callable[..., Any]:
    """Adapt `(cls, ctx)` op to `(p, *, db, request, ctx)` handler signature."""

    async def core(p=None, *, db=None, request=None, ctx: Dict[str, Any] | None = None):
        ctx = _Ctx.ensure(request=request, db=db, seed=ctx)
        if p is not None:
            ctx["payload"] = p
        bound = func.__get__(table, table)
        res = await _maybe_await(bound(ctx))
        return res if res is not None else ctx.get("result")

    core.__name__ = getattr(func, "__name__", "core")
    core.__qualname__ = getattr(func, "__qualname__", core.__name__)
    return core


def collect_decorated_ops(table: type) -> list[OpSpec]:
    """Scan MRO for ctx-only op declarations (@op_ctx) and build OpSpecs."""

    logger.info("Collecting decorated ops for %s", table.__name__)
    out: list[OpSpec] = []

    for base in reversed(table.__mro__):
        names = list(getattr(base, "__dict__", {}).keys())
        for name in dir(base):
            if name not in names:
                names.append(name)
        for name in names:
            attr = getattr(base, name, None)
            func = _unwrap(attr)
            decl: _OpDecl | None = getattr(func, "__autoapi_op_decl__", None)
            if not decl:
                continue

            target = decl.target or "custom"
            arity = decl.arity or _infer_arity(target)
            persist = _normalize_persist(decl.persist)
            alias = decl.alias or name

            expose_kwargs: dict[str, Any] = {}
            extra: dict[str, Any] = {}
            if decl.rest is not None:
                expose_kwargs["expose_routes"] = bool(decl.rest)
            elif alias != target and target in {
                "read",
                "update",
                "delete",
                "list",
                "clear",
            }:
                expose_kwargs["expose_routes"] = False

            spec = OpSpec(
                table=table,
                alias=alias,
                target=target,
                arity=arity,
                persist=persist,
                handler=_wrap_ctx_core(table, func),
                request_model=decl.request_schema,
                response_model=decl.response_schema,
                hooks=(),
                status_code=decl.status_code,
                extra=extra,
                **expose_kwargs,
            )
            out.append(spec)

    logger.debug("Collected %d ops for %s", len(out), table.__name__)
    return out


__all__ = ["collect_decorated_ops", "alias_map_for", "apply_alias"]
