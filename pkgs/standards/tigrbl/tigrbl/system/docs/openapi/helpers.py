"""Helper utilities for stdapi OpenAPI schema generation."""

from __future__ import annotations

import inspect
from typing import Any, Iterable, get_args, get_origin

from ....core.crud.params import Param
from ....core.resolver import (
    annotation_marker as _annotation_marker,
    split_annotated as _split_annotated,
)
from ....deps._stdapi_types import Route


def _normalize_schema_refs(node: Any) -> Any:
    if isinstance(node, dict):
        normalized: dict[str, Any] = {}
        for key, value in node.items():
            if (
                key == "$ref"
                and isinstance(value, str)
                and value.startswith("#/$defs/")
            ):
                normalized[key] = value.replace("#/$defs/", "#/components/schemas/")
                continue
            normalized[key] = _normalize_schema_refs(value)
        return normalized
    if isinstance(node, list):
        return [_normalize_schema_refs(item) for item in node]
    return node


def _schema_from_model(
    model: Any, components_schemas: dict[str, Any] | None = None
) -> dict[str, Any]:
    try:
        import pydantic

        if isinstance(model, type) and issubclass(model, pydantic.BaseModel):
            schema = model.model_json_schema(
                ref_template="#/components/schemas/{model}"
            )
            schema = _normalize_schema_refs(schema)
            defs = schema.pop("$defs", None)
            if isinstance(defs, dict) and components_schemas is not None:
                for name, definition in defs.items():
                    components_schemas.setdefault(
                        name, _normalize_schema_refs(definition)
                    )
            if components_schemas is None:
                return schema  # type: ignore[no-any-return]

            schema_name = str(schema.get("title") or model.__name__)
            components_schemas.setdefault(schema_name, schema)
            return {"$ref": f"#/components/schemas/{schema_name}"}
    except Exception:
        pass

    origin = getattr(model, "__origin__", None)
    if origin in (list, tuple, set):
        item = model.__args__[0] if getattr(model, "__args__", None) else Any
        return {"type": "array", "items": _schema_from_model(item, components_schemas)}
    return {"type": "object"}


def _resolve_component_schema_ref(
    schema: dict[str, Any],
    components_schemas: dict[str, Any],
) -> dict[str, Any]:
    ref = schema.get("$ref")
    if not isinstance(ref, str) or not ref.startswith("#/components/schemas/"):
        return schema

    schema_name = ref.rsplit("/", maxsplit=1)[-1]
    component = components_schemas.get(schema_name)
    if not isinstance(component, dict):
        return schema
    return component


def _schema_from_annotation(
    annotation: Any, components_schemas: dict[str, Any]
) -> dict[str, Any]:
    annotation, _ = _split_annotated(annotation)

    if annotation is Any:
        return {"type": "object"}

    origin = get_origin(annotation)
    if origin in (list, tuple, set):
        args = get_args(annotation)
        item_annotation = args[0] if args else Any
        return {
            "type": "array",
            "items": _schema_from_annotation(item_annotation, components_schemas),
        }

    if origin is not None:
        args = [arg for arg in get_args(annotation) if arg is not type(None)]
        if len(args) == 1:
            return _schema_from_annotation(args[0], components_schemas)

    if annotation in (dict,):
        return {"type": "object"}

    try:
        from collections.abc import Mapping as _Mapping

        if isinstance(annotation, type) and issubclass(annotation, _Mapping):
            return {"type": "object"}
    except Exception:
        pass

    return _schema_from_model(annotation, components_schemas)


def _request_schema_from_handler(
    route: Route, components_schemas: dict[str, Any]
) -> dict[str, Any] | None:
    handler = getattr(route, "handler", None)
    if handler is None:
        return None

    try:
        signature = inspect.signature(handler)
    except Exception:
        return None

    for param in signature.parameters.values():
        if param.kind not in (
            inspect.Parameter.POSITIONAL_ONLY,
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            inspect.Parameter.KEYWORD_ONLY,
        ):
            continue

        annotation, extras = _split_annotated(param.annotation)
        marker = _annotation_marker(extras, Param)
        if marker is None or marker.location != "body":
            continue

        return _schema_from_annotation(annotation, components_schemas)

    return None


def _security_from_dependencies(deps: Iterable[Any]) -> list[dict[str, list[str]]]:
    security: list[dict[str, list[str]]] = []
    for dependency in _extract_security_dependencies(deps):
        if _is_http_bearer_dependency(dependency):
            scheme_name = getattr(dependency, "scheme_name", None) or "HTTPBearer"
            security.append({scheme_name: []})
    return security


def _security_schemes_from_dependencies(deps: Iterable[Any]) -> dict[str, Any]:
    schemes: dict[str, Any] = {}
    for dependency in _extract_security_dependencies(deps):
        if _is_http_bearer_dependency(dependency):
            scheme_name = getattr(dependency, "scheme_name", None) or "HTTPBearer"
            schemes[scheme_name] = {"type": "http", "scheme": "bearer"}
    return schemes


def _extract_security_dependencies(deps: Iterable[Any]) -> Iterable[Any]:
    seen: set[int] = set()
    for dep in deps:
        yield from _iter_security_dependencies(dep, seen)


def _iter_security_dependencies(dep: Any, seen: set[int]) -> Iterable[Any]:
    if dep is None:
        return

    dep_id = id(dep)
    if dep_id in seen:
        return
    seen.add(dep_id)

    dependency = getattr(dep, "dependency", None)
    if dependency is not None:
        yield from _iter_security_dependencies(dependency, seen)
        return

    yield dep

    if not callable(dep):
        return

    try:
        signature = inspect.signature(dep)
    except (TypeError, ValueError):
        return

    for param in signature.parameters.values():
        default = param.default
        if default is inspect._empty:
            continue
        yield from _iter_security_dependencies(default, seen)


def _is_http_bearer_dependency(dep: Any) -> bool:
    return dep.__class__.__name__ == "HTTPBearer"
