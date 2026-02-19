"""Handler argument resolution helpers for API routing."""

from __future__ import annotations

import inspect
from typing import Any

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
from ..runtime.dependencies import DependencyToken
from ..security.dependencies import Dependency


async def resolve_route_dependencies(router: Any, route: Any, req: Any) -> None:
    """Deprecated compatibility shim.

    Dependency execution now occurs in runtime dispatch, not during resolution.
    """

    del router, route, req
    return None


async def resolve_handler_kwargs(router: Any, route: Any, req: Any) -> dict[str, Any]:
    del router
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
            kwargs[name] = DependencyToken(dependency=dep)
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


__all__ = ["resolve_route_dependencies", "resolve_handler_kwargs"]
