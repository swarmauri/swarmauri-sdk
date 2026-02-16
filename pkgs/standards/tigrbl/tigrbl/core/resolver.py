"""Core resolver helpers shared by API routing and OpenAPI tooling."""

from __future__ import annotations

from typing import Annotated, Any, Iterable, get_args, get_origin

from ..core.crud.params import Param
from ..runtime.status.exceptions import HTTPException
from ..runtime.status.mappings import status
from ..requests import Request


def split_annotated(annotation: Any) -> tuple[Any, tuple[Any, ...]]:
    if get_origin(annotation) is Annotated:
        args = get_args(annotation)
        if args:
            return args[0], tuple(args[1:])
    return annotation, ()


def annotation_marker(extras: Iterable[Any], marker_type: type[Any]) -> Any | None:
    for extra in extras:
        if isinstance(extra, marker_type):
            return extra
    return None


def is_request_annotation(annotation: Any) -> bool:
    if annotation is Request:
        return True
    if isinstance(annotation, str):
        normalized = annotation.strip().strip("\"'")
        return normalized.rsplit(".", maxsplit=1)[-1] == "Request"
    return False


def load_body(req: Request) -> Any:
    try:
        return req.json_sync()
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid JSON: {exc}",
        ) from exc


def extract_param_value(
    marker: Param,
    req: Request,
    param_name: str,
    body_cache: Any | None,
) -> tuple[Any, bool]:
    alias = marker.alias or param_name
    if marker.location == "query":
        if alias in req.query_params:
            return req.query_params[alias], True
        return None, False
    if marker.location == "path":
        if alias in req.path_params:
            return req.path_params[alias], True
        return None, False
    if marker.location == "header":
        key = alias.lower()
        if key in req.headers:
            return req.headers[key], True
        return None, False
    if marker.location == "body":
        if body_cache is None:
            body_cache = load_body(req)
        if isinstance(body_cache, dict):
            if marker.alias is None and param_name == "body":
                return body_cache, True
            if alias in body_cache:
                return body_cache[alias], True
            if param_name in body_cache:
                return body_cache[param_name], True
            if marker.alias is None:
                return body_cache, True
        elif body_cache is not None:
            return body_cache, True
    return None, False
