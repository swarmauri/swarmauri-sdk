from __future__ import annotations

import inspect
from typing import Any, Callable

from ....core.crud.params import Param
from ....mapping.core_resolver import (
    annotation_marker,
    extract_param_value,
    is_request_annotation,
    split_annotated,
)
from ....runtime.status.exceptions import HTTPException
from ....runtime.status.mappings import status
from ....security.dependencies import Dependency
from ... import events as _ev

ANCHOR = _ev.DEP_SECURITY


async def invoke_dependency(router: Any, dep: Callable[..., Any], req: Any) -> Any:
    provider = getattr(router, "dependency_overrides_provider", None) or router
    overrides = getattr(provider, "dependency_overrides", {})
    dep = overrides.get(dep, dep)
    kwargs: dict[str, Any] = {}

    for name, param in inspect.signature(dep).parameters.items():
        base_annotation, extras = split_annotated(param.annotation)
        dependency_marker = annotation_marker(extras, Dependency)
        param_marker = annotation_marker(extras, Param)

        if is_request_annotation(base_annotation) or name == "request":
            kwargs[name] = req
        elif isinstance(param.default, Dependency) or dependency_marker is not None:
            child = (
                param.default.dependency
                if isinstance(param.default, Dependency)
                else dependency_marker.dependency
            )
            kwargs[name] = await invoke_dependency(router, child, req)
        elif isinstance(param.default, Param) or param_marker is not None:
            marker = param.default if isinstance(param.default, Param) else param_marker
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
        elif name in req.path_params:
            kwargs[name] = req.path_params[name]
        elif name in req.query_params:
            kwargs[name] = req.query_params[name]
        elif param.default is not inspect._empty:
            kwargs[name] = param.default

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


async def run(dep: object | None, ctx: Any) -> Any:
    fn = getattr(dep, "dependency", dep)
    if not callable(fn):
        return None

    ctx_map = ctx if isinstance(ctx, dict) else {}
    req = getattr(ctx, "request", None) or ctx_map.get("request") or ctx_map.get("req")
    router = getattr(ctx, "router", None) or ctx_map.get("router")

    if req is not None and router is not None:
        return await invoke_dependency(router, fn, req)

    try:
        rv = fn(ctx)
    except TypeError:
        rv = fn()
    if inspect.isawaitable(rv):
        return await rv
    return rv
