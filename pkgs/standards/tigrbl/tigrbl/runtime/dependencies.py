"""Dependency resolution and execution helpers for runtime/app layers."""

from __future__ import annotations

import inspect
from typing import Any

from ..core.crud.params import Param
from ..mapping.core_resolver import (
    annotation_marker,
    extract_param_value,
    is_request_annotation,
    split_annotated,
)
from ..runtime.atoms.deps_inject.runtime import (
    DependencyToken,
    execute_dependency_tokens,
    execute_route_dependencies,
    invoke_dependency,
)
from ..security.dependencies import Dependency


async def resolve_handler_kwargs(router: Any, route: Any, req: Any) -> dict[str, Any]:
    """Resolve request-derived kwargs while deferring dependency execution."""
    del router
    kwargs: dict[str, Any] = {}
    body_cache: Any | None = None

    for name, param in inspect.signature(route.handler).parameters.items():
        base_annotation, extras = split_annotated(param.annotation)
        dep_marker = annotation_marker(extras, Dependency)
        param_marker = annotation_marker(extras, Param)

        if isinstance(param.default, Dependency) or dep_marker is not None:
            dep = (
                param.default.dependency
                if isinstance(param.default, Dependency)
                else dep_marker.dependency
            )
            kwargs[name] = DependencyToken(dep)
            continue

        if is_request_annotation(base_annotation) or name == "request":
            kwargs[name] = req
            continue

        if isinstance(param.default, Param) or param_marker is not None:
            marker = param.default if isinstance(param.default, Param) else param_marker
            value, found = extract_param_value(marker, req, name, body_cache)
            if found:
                kwargs[name] = value
            elif marker.required:
                continue
            else:
                kwargs[name] = marker.default
            continue

        if name in req.path_params:
            kwargs[name] = req.path_params[name]
        elif name in req.query_params:
            kwargs[name] = req.query_params[name]
        elif param.default is not inspect._empty:
            kwargs[name] = param.default

    return kwargs


__all__ = [
    "DependencyToken",
    "invoke_dependency",
    "execute_route_dependencies",
    "execute_dependency_tokens",
    "resolve_handler_kwargs",
]
