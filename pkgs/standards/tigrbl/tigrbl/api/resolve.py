"""Dependency resolution helpers for API routing."""

from __future__ import annotations

import inspect
from typing import Any, Callable

from ..core.crud.params import Param
from ..runtime.status.exceptions import HTTPException
from ..runtime.status.mappings import status

from ..core.resolver import (
    annotation_marker,
    extract_param_value,
    is_request_annotation,
    load_body,
    split_annotated,
)
from ..security.dependencies import Dependency


async def resolve_route_dependencies(router: Any, route: Any, req: Any) -> None:
    if router._is_metadata_route(route):
        return
    for dep in route.dependencies or []:
        dep_callable = dep.dependency if isinstance(dep, Dependency) else dep
        await invoke_dependency(router, dep_callable, req)


async def resolve_handler_kwargs(router: Any, route: Any, req: Any) -> dict[str, Any]:
    sig = inspect.signature(route.handler)
    kwargs: dict[str, Any] = {}
    body_cache: Any | None = None

    for name, param in sig.parameters.items():
        base_annotation, extras = split_annotated(param.annotation)
        dependency_marker = annotation_marker(extras, Dependency)
        param_marker = annotation_marker(extras, Param)
        if param.kind is inspect.Parameter.VAR_KEYWORD:
            kwargs.update(req.path_params)
            continue
        if name in req.path_params:
            kwargs[name] = req.path_params[name]
            continue
        if is_request_annotation(base_annotation) or name == "request":
            kwargs[name] = req
            continue
        if base_annotation is inspect._empty and name.endswith("request"):
            kwargs[name] = req
            continue
        default = param.default
        if isinstance(default, Dependency) or dependency_marker is not None:
            dep = default.dependency if isinstance(default, Dependency) else None
            dep = dep or dependency_marker.dependency
            kwargs[name] = await invoke_dependency(router, dep, req)
            continue
        if isinstance(default, Param) or param_marker is not None:
            marker = default if isinstance(default, Param) else param_marker
            value, found = extract_param_value(marker, req, name, body_cache)
            if found:
                kwargs[name] = value
                if marker.location == "body":
                    body_cache = value
                continue
            if marker.required:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Missing required parameter: {marker.alias or name}",
                )
            kwargs[name] = marker.default
            continue
        if default is inspect._empty:
            if body_cache is None:
                body_cache = load_body(req)
            if isinstance(body_cache, dict) and name in body_cache:
                kwargs[name] = body_cache[name]
                continue
        if default is not inspect._empty:
            kwargs[name] = default
    return kwargs


async def invoke_dependency(router: Any, dep: Callable[..., Any], req: Any) -> Any:
    sig = inspect.signature(dep)
    kwargs: dict[str, Any] = {}
    for name, param in sig.parameters.items():
        base_annotation, extras = split_annotated(param.annotation)
        dependency_marker = annotation_marker(extras, Dependency)
        param_marker = annotation_marker(extras, Param)
        if is_request_annotation(base_annotation) or name == "request":
            kwargs[name] = req
            continue
        if isinstance(param.default, Dependency) or dependency_marker is not None:
            child = (
                param.default.dependency
                if isinstance(param.default, Dependency)
                else dependency_marker.dependency
            )
            kwargs[name] = await invoke_dependency(router, child, req)
            continue
        if isinstance(param.default, Param) or param_marker is not None:
            marker = param.default if isinstance(param.default, Param) else param_marker
            value, found = extract_param_value(marker, req, name, None)
            if found:
                kwargs[name] = value
                continue
            if marker.required:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Missing required parameter: {marker.alias or name}",
                )
            kwargs[name] = marker.default
            continue
        if name in req.path_params:
            kwargs[name] = req.path_params[name]
            continue
        if name in req.query_params:
            kwargs[name] = req.query_params[name]
            continue
        if param.default is inspect._empty:
            continue
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
        out = await out
    return out
