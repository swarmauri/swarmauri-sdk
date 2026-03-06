"""Core resolver helpers shared by API routing and OpenAPI tooling."""

from __future__ import annotations

from typing import Annotated, Any, Iterable, get_args, get_origin

from tigrbl_ops_oltp.crud.params import Param
from tigrbl_runtime.runtime.status.exceptions import HTTPException
from tigrbl_runtime.runtime.status.mappings import status
from tigrbl_typing.protocols import RequestLike


def _request_field(req: RequestLike | dict[str, Any], name: str) -> Any:
    if isinstance(req, dict):
        return req.get(name)
    return getattr(req, name, None)


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
    if isinstance(annotation, type) and annotation.__name__ == "Request":
        return True
    if isinstance(annotation, str):
        normalized = annotation.strip().strip("\"'")
        return normalized.rsplit(".", maxsplit=1)[-1] == "Request"
    return False


def load_body(req: RequestLike) -> Any:
    if isinstance(req, dict):
        body = req.get("body", req.get("payload"))
        if body is not None:
            return body
    try:
        return req.json_sync()
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid JSON: {exc}",
        ) from exc


def extract_param_value(
    marker: Param,
    req: RequestLike,
    param_name: str,
    body_cache: Any | None,
) -> tuple[Any, bool]:
    alias = marker.alias or param_name
    query_params = _request_field(req, "query_params") or {}
    path_params = _request_field(req, "path_params") or {}
    headers = _request_field(req, "headers") or {}

    if marker.location == "query":
        if alias in query_params:
            return query_params[alias], True
        return None, False
    if marker.location == "path":
        if alias in path_params:
            return path_params[alias], True
        return None, False
    if marker.location == "header":
        key = alias.lower()
        if key in headers:
            return headers[key], True
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
