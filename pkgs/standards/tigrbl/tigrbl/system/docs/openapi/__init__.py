"""OpenAPI helpers and mount utilities."""

from .helpers import (
    _extract_security_dependencies,
    _is_http_bearer_dependency,
    _iter_security_dependencies,
    _normalize_schema_refs,
    _request_schema_from_handler,
    _resolve_component_schema_ref,
    _schema_from_annotation,
    _schema_from_model,
    _security_from_dependencies,
    _security_schemes_from_dependencies,
)
from .mount import mount_openapi
from .schema import openapi

build_openapi = openapi

__all__ = [
    "openapi",
    "build_openapi",
    "mount_openapi",
    "_extract_security_dependencies",
    "_is_http_bearer_dependency",
    "_iter_security_dependencies",
    "_normalize_schema_refs",
    "_request_schema_from_handler",
    "_resolve_component_schema_ref",
    "_schema_from_annotation",
    "_schema_from_model",
    "_security_from_dependencies",
    "_security_schemes_from_dependencies",
]
