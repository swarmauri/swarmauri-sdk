"""Handler argument resolution helpers for router dispatch."""

from __future__ import annotations

import inspect
from typing import Any

from ..core.crud.params import Param
from ..core.resolver import (
    annotation_marker,
    extract_param_value,
    is_request_annotation,
    load_body,
    split_annotated,
)
from ..runtime.dependencies import DependencyToken
from ..runtime.status.exceptions import HTTPException
from ..runtime.status.mappings import status
from ..security.dependencies import Dependency


async def resolve_handler_kwargs(router: Any, route: Any, req: Any) -> dict[str, Any]:
    del router
    body_cache: Any | None = None
    kwargs: dict[str, Any] = {}

    for name, param in inspect.signature(route.handler).parameters.items():
        base_annotation, extras = split_annotated(param.annotation)
        dependency_marker = annotation_marker(extras, Dependency)
        param_marker = annotation_marker(extras, Param)
        default = param.default

        if param.kind is inspect.Parameter.VAR_KEYWORD:
            kwargs.update(req.path_params)
        elif name in req.path_params:
            kwargs[name] = req.path_params[name]
        elif is_request_annotation(base_annotation) or name == "request":
            kwargs[name] = req
        elif base_annotation is inspect._empty and name.endswith("request"):
            kwargs[name] = req
        elif isinstance(default, Dependency) or dependency_marker is not None:
            dep = default.dependency if isinstance(default, Dependency) else None
            kwargs[name] = DependencyToken(
                dependency=dep or dependency_marker.dependency
            )
        elif isinstance(default, Param) or param_marker is not None:
            marker = default if isinstance(default, Param) else param_marker
            value, found = extract_param_value(marker, req, name, body_cache)
            if found:
                kwargs[name] = value
                if marker.location == "body":
                    body_cache = value
            elif marker.required:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Missing required parameter: {marker.alias or name}",
                )
            else:
                kwargs[name] = marker.default
        elif default is inspect._empty:
            if body_cache is None:
                body_cache = load_body(req)
            if isinstance(body_cache, dict) and name in body_cache:
                kwargs[name] = body_cache[name]
        else:
            kwargs[name] = default

    return kwargs


__all__ = ["resolve_handler_kwargs"]
