from __future__ import annotations

from ...types import Atom, Ctx, GuardedCtx
from ...stages import Planned, Guarded

import inspect
from functools import lru_cache
from typing import Any, Callable

from ._param_resolver import (
    Param,
    annotation_marker,
    extract_param_value,
    is_request_annotation,
    split_annotated,
)
from tigrbl_typing.status.exceptions import HTTPException
from tigrbl_typing.status.mappings import status
from ...types import DependencyLike, is_dependency_like
from ... import events as _ev

ANCHOR = _ev.DEP_SECURITY


@lru_cache(maxsize=512)
def _signature_params(fn: Callable[..., Any]) -> tuple[tuple[Any, ...], ...]:
    sig = inspect.signature(fn)
    out: list[tuple[Any, ...]] = []
    empty = inspect._empty
    for name, param in sig.parameters.items():
        base_annotation, extras = split_annotated(param.annotation)
        out.append(
            (
                name,
                base_annotation,
                annotation_marker(extras, DependencyLike),
                annotation_marker(extras, Param),
                param.default,
                base_annotation is empty and name.endswith("request"),
                is_request_annotation(base_annotation)
                or name == "request"
                or name.lower().endswith("request"),
            )
        )
    return tuple(out)


def _uncached_signature_params(fn: Callable[..., Any]) -> tuple[tuple[Any, ...], ...]:
    sig = inspect.signature(fn)
    out: list[tuple[Any, ...]] = []
    empty = inspect._empty
    for name, param in sig.parameters.items():
        base_annotation, extras = split_annotated(param.annotation)
        out.append(
            (
                name,
                base_annotation,
                annotation_marker(extras, DependencyLike),
                annotation_marker(extras, Param),
                param.default,
                base_annotation is empty and name.endswith("request"),
                is_request_annotation(base_annotation)
                or name == "request"
                or name.lower().endswith("request"),
            )
        )
    return tuple(out)


async def invoke_dependency(router: Any, dep: Callable[..., Any], req: Any) -> Any:
    provider = getattr(router, "dependency_overrides_provider", None) or router
    overrides = getattr(provider, "dependency_overrides", {})
    try:
        dep = overrides.get(dep, dep)
    except TypeError:
        dep = dep

    try:
        params = _signature_params(dep)
    except TypeError:
        params = _uncached_signature_params(dep)
    if not params:
        out = dep()
        if inspect.isgenerator(out):
            try:
                value = next(out)
            except StopIteration:
                return None
            cleanups = getattr(req.state, "_dependency_cleanups", None)
            if isinstance(cleanups, list):
                cleanups.append(out.close)
            return value
        if inspect.isasyncgen(out):
            try:
                value = await anext(out)
            except StopAsyncIteration:
                return None
            cleanups = getattr(req.state, "_dependency_cleanups", None)
            if isinstance(cleanups, list):
                cleanups.append(out.aclose)
            return value
        if inspect.isawaitable(out):
            return await out
        return out

    kwargs: dict[str, Any] = {}
    path_params = req.path_params
    query_params = req.query_params
    for (
        name,
        _base_annotation,
        dependency_marker,
        param_marker,
        default,
        request_by_name,
        request_annotation,
    ) in params:
        if request_annotation or request_by_name:
            kwargs[name] = req
        elif is_dependency_like(default) or dependency_marker is not None:
            child = (
                default.dependency
                if is_dependency_like(default)
                else dependency_marker.dependency
            )
            kwargs[name] = await invoke_dependency(router, child, req)
        elif isinstance(default, Param) or param_marker is not None:
            marker = default if isinstance(default, Param) else param_marker
            value, found = extract_param_value(marker, req, name, None)
            if found:
                kwargs[name] = value
            elif marker.required:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Missing required parameter: {marker.alias or name}",
                )
            else:
                kwargs[name] = marker.default
        elif name in path_params:
            kwargs[name] = path_params[name]
        elif name in query_params:
            kwargs[name] = query_params[name]
        elif default is not inspect._empty:
            kwargs[name] = default

    out = dep(**kwargs)
    if inspect.isgenerator(out):
        try:
            value = next(out)
        except StopIteration:
            return None
        cleanups = getattr(req.state, "_dependency_cleanups", None)
        if isinstance(cleanups, list):
            cleanups.append(out.close)
        return value

    if inspect.isasyncgen(out):
        try:
            value = await anext(out)
        except StopAsyncIteration:
            return None
        cleanups = getattr(req.state, "_dependency_cleanups", None)
        if isinstance(cleanups, list):
            cleanups.append(out.aclose)
        return value

    if inspect.isawaitable(out):
        return await out
    return out


async def _run(dep: object | None, ctx: Any) -> Any:
    fn = getattr(dep, "dependency", dep)
    if not callable(fn):
        return None

    ctx_map = ctx if isinstance(ctx, dict) else {}
    req = getattr(ctx, "request", None) or ctx_map.get("request") or ctx_map.get("req")
    router = getattr(ctx, "router", None) or ctx_map.get("router")

    if req is not None and router is not None:
        value = await invoke_dependency(router, fn, req)
        if getattr(fn, "__tigrbl_require_auth__", False) and value is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unauthorized",
            )
        return value

    try:
        rv = fn(ctx)
    except TypeError:
        rv = fn()
    if inspect.isawaitable(rv):
        return await rv
    return rv


class AtomImpl(Atom[Planned, Guarded]):
    name = "dep.security"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Planned]) -> Ctx[Guarded]:
        await _run(obj, ctx)
        return ctx.promote(GuardedCtx)


INSTANCE = AtomImpl()

__all__ = ["ANCHOR", "INSTANCE"]
