"""Runtime dependency execution helpers.

Dependency callables execute during runtime invocation, not resolution.
"""

from __future__ import annotations

import inspect
from dataclasses import dataclass
from typing import Any, Callable

from ..core.crud.params import Param
from ..core.resolver import (
    annotation_marker,
    extract_param_value,
    is_request_annotation,
    split_annotated,
)
from ..runtime.status.exceptions import HTTPException
from ..runtime.status.mappings import status
from ..security.dependencies import Dependency


@dataclass(frozen=True)
class DependencyToken:
    dependency: Callable[..., Any]


async def invoke_dependency(router: Any, dep: Callable[..., Any], req: Any) -> Any:
    provider = getattr(router, "dependency_overrides_provider", None) or router
    overrides = getattr(provider, "dependency_overrides", {})
    dep = overrides.get(dep, dep)
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


async def execute_route_dependencies(router: Any, route: Any, req: Any) -> None:
    if router._is_metadata_route(route):
        return
    for dep in route.dependencies or []:
        dep_callable = dep.dependency if isinstance(dep, Dependency) else dep
        await invoke_dependency(router, dep_callable, req)


async def execute_dependency_tokens(
    router: Any, kwargs: dict[str, Any], req: Any
) -> dict[str, Any]:
    resolved: dict[str, Any] = {}
    for name, value in kwargs.items():
        if isinstance(value, DependencyToken):
            resolved[name] = await invoke_dependency(router, value.dependency, req)
        else:
            resolved[name] = value
    return resolved


__all__ = [
    "DependencyToken",
    "invoke_dependency",
    "execute_route_dependencies",
    "execute_dependency_tokens",
]
