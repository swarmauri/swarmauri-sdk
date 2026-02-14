"""Security primitives and OpenAPI security scheme helpers for Tigrbl."""

from __future__ import annotations

from typing import Any

from .dependencies import Dependency, Depends, Security
from .schemes import (
    APIKey,
    HTTPAuthorizationCredentials,
    HTTPBearer,
    MutualTLS,
    OAuth2,
    OpenAPISecurityDependency,
    OpenIdConnect,
    validate_openapi_security_scheme,
)


def security_requirement_from_dependency(dep: Any) -> dict[str, list[str]] | None:
    requirement = getattr(dep, "openapi_security_requirement", None)
    if callable(requirement):
        out = requirement()
        if isinstance(out, dict):
            return out
    return None


def security_scheme_from_dependency(dep: Any) -> tuple[str, dict[str, Any]] | None:
    requirement = security_requirement_from_dependency(dep)
    if not requirement:
        return None

    scheme_name = next(iter(requirement.keys()), None)
    if not scheme_name:
        return None

    scheme_factory = getattr(dep, "openapi_security_scheme", None)
    if not callable(scheme_factory):
        return None

    scheme = scheme_factory()
    if not isinstance(scheme, dict):
        return None

    validate_openapi_security_scheme(scheme)
    return scheme_name, scheme


__all__ = [
    "Dependency",
    "Depends",
    "Security",
    "HTTPAuthorizationCredentials",
    "OpenAPISecurityDependency",
    "HTTPBearer",
    "APIKey",
    "OAuth2",
    "OpenIdConnect",
    "MutualTLS",
    "security_requirement_from_dependency",
    "security_scheme_from_dependency",
]
