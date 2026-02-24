from __future__ import annotations

import inspect
from types import SimpleNamespace
from typing import Any, Callable, Dict, Optional, cast

from ... import trace as _trace


def _ctx_value(ctx: Any, key: str) -> Any:
    aliases = ("req",) if key == "request" else (("model",) if key == "table" else ())
    attr = getattr(ctx, key, None)
    if attr is not None:
        return attr
    for alias in aliases:
        alias_attr = getattr(ctx, alias, None)
        if alias_attr is not None:
            return alias_attr
    if isinstance(ctx, dict):
        value = ctx.get(key)
        if value is not None:
            return value
        for alias in aliases:
            alias_value = ctx.get(alias)
            if alias_value is not None:
                return alias_value
    return None


def _op_spec_from_ctx(ctx: Any) -> Any | None:
    table = _ctx_value(ctx, "table")
    alias = _ctx_value(ctx, "op") or _ctx_value(ctx, "method")
    if table is None or not alias:
        return None
    by_alias = getattr(getattr(table, "ops", SimpleNamespace()), "by_alias", {})
    specs = by_alias.get(alias) or ()
    return specs[0] if specs else None


def _dep_callable(dep: Any) -> Optional[Callable[..., Any]]:
    if callable(dep):
        return cast(Callable[..., Any], dep)
    inner = getattr(dep, "dependency", None)
    if callable(inner):
        return cast(Callable[..., Any], inner)
    return None


async def _resolve_dependency_default(default: Any, ctx: Any) -> Any:
    dep = getattr(default, "dependency", None)
    if not callable(dep):
        return default

    request = _ctx_value(ctx, "request")
    if request is None:
        return default

    try:
        rv = dep(request)
    except TypeError:
        return default

    if hasattr(rv, "__await__"):
        return await cast(Any, rv)
    return rv


async def _invoke_kwargs(
    fn: Callable[..., Any], ctx: Any
) -> tuple[Dict[str, Any], bool]:
    ctx_contains = ctx.__contains__ if isinstance(ctx, dict) else lambda _key: False
    kwargs: Dict[str, Any] = {}
    has_required = False
    for p in inspect.signature(fn).parameters.values():
        if p.kind in (
            inspect.Parameter.POSITIONAL_ONLY,
            inspect.Parameter.VAR_POSITIONAL,
            inspect.Parameter.VAR_KEYWORD,
        ):
            continue
        if p.name == "ctx":
            kwargs[p.name] = ctx
        elif p.name in ("request", "db", "table", "op", "payload"):
            kwargs[p.name] = _ctx_value(ctx, p.name)
        elif p.name == "model":
            kwargs[p.name] = _ctx_value(ctx, "table")
        elif ctx_contains(p.name):
            kwargs[p.name] = ctx[p.name]
        elif p.default is not inspect._empty and getattr(p.default, "dependency", None):
            kwargs[p.name] = await _resolve_dependency_default(p.default, ctx)
        elif p.default is inspect._empty:
            has_required = True
    return kwargs, has_required


def dep_name(dep: Any) -> str:
    explicit_name = getattr(dep, "__tigrbl_dep_name__", None)
    if isinstance(explicit_name, str) and explicit_name:
        return explicit_name

    fn = _dep_callable(dep)
    target = fn if fn is not None else dep

    explicit_target_name = getattr(target, "__tigrbl_dep_name__", None)
    if isinstance(explicit_target_name, str) and explicit_target_name:
        return explicit_target_name

    if fn is not None:
        module = getattr(fn, "__module__", None)
        qualname = getattr(fn, "__qualname__", None)
        if (
            isinstance(module, str)
            and module
            and isinstance(qualname, str)
            and qualname
        ):
            return f"{module}.{qualname}"

    obj_type = type(target)
    module = getattr(obj_type, "__module__", None)
    qualname = getattr(obj_type, "__qualname__", None)
    if isinstance(module, str) and module and isinstance(qualname, str) and qualname:
        return f"{module}.{qualname}"

    return str(dep)


async def run_deps(ctx: Any, *, kind: str) -> None:
    sp = _op_spec_from_ctx(ctx)
    if sp is None:
        return
    deps = getattr(sp, "secdeps", ()) if kind == "secdep" else getattr(sp, "deps", ())
    for dep in deps or ():
        fn = _dep_callable(dep)
        if fn is None:
            continue
        label = f"{kind}:{dep_name(dep)}"
        seq = _trace.start(ctx, label)
        try:
            kwargs, has_required = await _invoke_kwargs(fn, ctx)
            rv = fn(ctx) if (has_required and not kwargs) else fn(**kwargs)
        except (TypeError, ValueError):
            rv = fn(ctx)
        try:
            if hasattr(rv, "__await__"):
                rv = await cast(Any, rv)
            if kind == "secdep" and rv is not None:
                if isinstance(ctx, dict):
                    ctx["auth_context"] = rv
                else:
                    setattr(ctx, "auth_context", rv)
            _trace.end(ctx, seq)
        except Exception as exc:
            _trace.attach_error(ctx, seq, exc)
            _trace.end(ctx, seq, status=_trace.ERROR)
            raise
