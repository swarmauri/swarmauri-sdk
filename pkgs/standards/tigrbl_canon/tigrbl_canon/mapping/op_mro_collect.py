from __future__ import annotations

import logging
import inspect
from functools import lru_cache
from typing import Any, Callable, Dict

from tigrbl_concrete._concrete._op import Op as OpSpec
from tigrbl.decorators.op import _maybe_await, _normalize_persist, _unwrap
from tigrbl_runtime.runtime.executor import _Ctx

logger = logging.getLogger("uvicorn")


def _merge_mro_dict(cls: type, attr: str) -> Dict[str, Any]:
    merged: Dict[str, Any] = {}
    for base in reversed(cls.__mro__):
        merged.update(getattr(base, attr, {}) or {})
    return merged


@lru_cache(maxsize=None)
def mro_alias_map_for(table: type) -> Dict[str, str]:
    """Collect alias overrides across the table's MRO."""
    return _merge_mro_dict(table, "__tigrbl_aliases__")


def _wrap_ctx_core(table: type, func: Callable[..., Any]) -> Callable[..., Any]:
    """Adapt `(cls, ctx)` op to `(p, *, db, request, ctx)` handler signature."""

    async def core(p=None, *, db=None, request=None, ctx: Dict[str, Any] | None = None):
        ctx = _Ctx.ensure(request=request, db=db, seed=ctx)
        if p is not None:
            ctx["payload"] = p
        bound = func.__get__(table, table)
        sig = inspect.signature(bound)
        kwargs: Dict[str, Any] = {}
        args: list[Any] = []
        if "ctx" in sig.parameters:
            kwargs["ctx"] = ctx
        elif "_ctx" in sig.parameters:
            kwargs["_ctx"] = ctx
        if "obj" in sig.parameters:
            kwargs["obj"] = getattr(ctx, "obj", None)
        elif "_obj" in sig.parameters:
            kwargs["_obj"] = getattr(ctx, "obj", None)
        if "objs" in sig.parameters:
            kwargs["objs"] = getattr(ctx, "objs", None)
        elif "_objs" in sig.parameters:
            kwargs["_objs"] = getattr(ctx, "objs", None)
        if "id" in sig.parameters:
            kwargs["id"] = getattr(ctx, "ident", None)
        elif "_id" in sig.parameters:
            kwargs["_id"] = getattr(ctx, "ident", None)

        # Backward compatibility for handlers declared as ``def op(cls, _ctx)``
        # or with a single unnamed positional parameter after class binding.
        if not kwargs:
            positional = [
                p
                for p in sig.parameters.values()
                if p.kind
                in {
                    inspect.Parameter.POSITIONAL_ONLY,
                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                }
                and p.default is inspect._empty
            ]
            if len(positional) == 1:
                args.append(ctx)

        res = await _maybe_await(bound(*args, **kwargs))
        return res if res is not None else ctx.get("result")

    core.__name__ = getattr(func, "__name__", "core")
    core.__qualname__ = getattr(func, "__qualname__", core.__name__)
    core.__tigrbl_ctx_wrapper__ = True
    return core


@lru_cache(maxsize=None)
def mro_collect_decorated_ops(table: type) -> list[OpSpec]:
    """Collect ctx-only op declarations across the table's MRO."""

    logger.info("Collecting decorated ops for %s", table.__name__)
    out: list[OpSpec] = []
    seen: set[str] = set()

    for base in table.__mro__:
        for name, attr in vars(base).items():
            if name in seen:
                continue
            func = _unwrap(attr)
            op_spec: OpSpec | None = getattr(func, "__tigrbl_op_spec__", None)
            if op_spec is None:
                op_spec = getattr(func, "__tigrbl_op_decl__", None)
            if op_spec is None:
                continue

            resolved_alias = op_spec.alias or name

            spec = OpSpec(
                table=table,
                alias=resolved_alias,
                target=op_spec.target,
                arity=op_spec.arity,
                persist=_normalize_persist(op_spec.persist),
                handler=_wrap_ctx_core(table, func),
                http_methods=getattr(op_spec, "http_methods", None),
                path_suffix=getattr(op_spec, "path_suffix", ""),
                tags=tuple(getattr(op_spec, "tags", ()) or ()),
                request_model=getattr(op_spec, "request_model", None),
                response_model=getattr(op_spec, "response_model", None),
                hooks=tuple(getattr(op_spec, "hooks", ()) or ()),
                status_code=getattr(op_spec, "status_code", None),
                expose_routes=getattr(op_spec, "expose_routes", None),
                expose_rpc=getattr(op_spec, "expose_rpc", None),
                expose_method=getattr(op_spec, "expose_method", None),
                engine=getattr(op_spec, "engine", None),
                response=getattr(op_spec, "response", None),
                returns=getattr(op_spec, "returns", None),
                rbac_guard_op=getattr(op_spec, "rbac_guard_op", None),
                core=getattr(op_spec, "core", None),
                core_raw=getattr(op_spec, "core_raw", None),
                extra=dict(getattr(op_spec, "extra", {}) or {}),
                deps=tuple(getattr(op_spec, "deps", ()) or ()),
                secdeps=tuple(getattr(op_spec, "secdeps", ()) or ()),
            )
            out.append(spec)
            seen.add(name)

    logger.debug("Collected %d ops for %s", len(out), table.__name__)
    return out


__all__ = ["mro_alias_map_for", "mro_collect_decorated_ops"]
