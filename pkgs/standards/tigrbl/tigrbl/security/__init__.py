"""Security primitives and OpenAPI security scheme helpers for Tigrbl."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from ..runtime.status.exceptions import HTTPException
from ..runtime.status.mappings import status

_VALID_SECURITY_SCHEME_TYPES = {
    "http",
    "apiKey",
    "oauth2",
    "openIdConnect",
    "mutualTLS",
}


@dataclass(frozen=True)
class HTTPAuthorizationCredentials:
    scheme: str
    credentials: str


class OpenAPISecurityDependency:
    """Base security dependency with OpenAPI document metadata."""

    def __init__(
        self,
        *,
        scheme_name: str,
        scheme: Mapping[str, Any],
        scopes: Sequence[str] | None = None,
        auto_error: bool = True,
    ) -> None:
        self.scheme_name = scheme_name
        self.auto_error = auto_error
        self._scheme = dict(scheme)
        self._scopes = list(scopes or [])
        _validate_openapi_security_scheme(self._scheme)

    def openapi_security_scheme(self) -> dict[str, Any]:
        return dict(self._scheme)

    def openapi_security_requirement(self) -> dict[str, list[str]]:
        return {self.scheme_name: list(self._scopes)}

    def __call__(self, request: Any) -> Any | None:
        return None


class HTTPBearer(OpenAPISecurityDependency):
    def __init__(
        self,
        auto_error: bool = True,
        *,
        scheme_name: str = "HTTPBearer",
        scheme: str = "bearer",
        bearer_format: str | None = None,
        description: str | None = None,
        scopes: Sequence[str] | None = None,
    ) -> None:
        payload: dict[str, Any] = {"type": "http", "scheme": scheme}
        if bearer_format is not None:
            payload["bearerFormat"] = bearer_format
        if description is not None:
            payload["description"] = description
        super().__init__(
            scheme_name=scheme_name,
            scheme=payload,
            scopes=scopes,
            auto_error=auto_error,
        )
        self.http_scheme = scheme

    def __call__(self, request: Any) -> HTTPAuthorizationCredentials | None:
        header = (getattr(request, "headers", None) or {}).get("authorization")
        if not header:
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Forbidden",
                )
            return None

        try:
            incoming_scheme, credentials = header.split(" ", 1)
        except ValueError:
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Forbidden",
                )
            return None

        if incoming_scheme.lower() != self.http_scheme.lower():
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Forbidden",
                )
            return None

        return HTTPAuthorizationCredentials(
            scheme=incoming_scheme,
            credentials=credentials,
        )


class APIKey(OpenAPISecurityDependency):
    def __init__(
        self,
        *,
        scheme_name: str = "ApiKeyAuth",
        name: str = "X-API-Key",
        in_: str = "header",
        description: str | None = None,
        scopes: Sequence[str] | None = None,
        auto_error: bool = True,
    ) -> None:
        payload: dict[str, Any] = {"type": "apiKey", "name": name, "in": in_}
        if description is not None:
            payload["description"] = description
        super().__init__(
            scheme_name=scheme_name,
            scheme=payload,
            scopes=scopes,
            auto_error=auto_error,
        )
        self.key_name = name
        self.key_in = in_

    def __call__(self, request: Any) -> str | None:
        headers = getattr(request, "headers", None) or {}
        query = getattr(request, "query_params", None) or {}
        value: str | None = None

        if self.key_in == "header":
            value = headers.get(self.key_name.lower()) or headers.get(self.key_name)
        elif self.key_in == "query":
            value = query.get(self.key_name)
        elif self.key_in == "cookie":
            cookie_header = headers.get("cookie", "")
            for part in cookie_header.split(";"):
                chunk = part.strip()
                if chunk.startswith(f"{self.key_name}="):
                    value = chunk.split("=", 1)[1]
                    break

        if value is None and self.auto_error:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Forbidden",
            )
        return value


class OAuth2(OpenAPISecurityDependency):
    def __init__(
        self,
        *,
        scheme_name: str = "OAuth2",
        flows: Mapping[str, Any],
        description: str | None = None,
        scopes: Sequence[str] | None = None,
        auto_error: bool = True,
    ) -> None:
        payload: dict[str, Any] = {"type": "oauth2", "flows": dict(flows)}
        if description is not None:
            payload["description"] = description
        super().__init__(
            scheme_name=scheme_name,
            scheme=payload,
            scopes=scopes,
            auto_error=auto_error,
        )


class OpenIdConnect(OpenAPISecurityDependency):
    def __init__(
        self,
        *,
        scheme_name: str = "OpenIdConnect",
        openid_connect_url: str,
        description: str | None = None,
        scopes: Sequence[str] | None = None,
        auto_error: bool = True,
    ) -> None:
        payload: dict[str, Any] = {
            "type": "openIdConnect",
            "openIdConnectUrl": openid_connect_url,
        }
        if description is not None:
            payload["description"] = description
        super().__init__(
            scheme_name=scheme_name,
            scheme=payload,
            scopes=scopes,
            auto_error=auto_error,
        )


class MutualTLS(OpenAPISecurityDependency):
    def __init__(
        self,
        *,
        scheme_name: str = "MutualTLS",
        description: str | None = None,
        scopes: Sequence[str] | None = None,
        auto_error: bool = True,
    ) -> None:
        payload: dict[str, Any] = {"type": "mutualTLS"}
        if description is not None:
            payload["description"] = description
        super().__init__(
            scheme_name=scheme_name,
            scheme=payload,
            scopes=scopes,
            auto_error=auto_error,
        )


def _validate_openapi_security_scheme(scheme: Mapping[str, Any]) -> None:
    scheme_type = scheme.get("type")
    if scheme_type not in _VALID_SECURITY_SCHEME_TYPES:
        raise ValueError(
            "OpenAPI security scheme 'type' must be one of: "
            f"{sorted(_VALID_SECURITY_SCHEME_TYPES)}"
        )

    if "scheme" in scheme and scheme_type != "http":
        raise ValueError("OpenAPI 'scheme' is only valid when type is 'http'.")

    if scheme_type == "http" and not scheme.get("scheme"):
        raise ValueError("OpenAPI type='http' requires a non-empty 'scheme'.")

    if scheme_type == "apiKey":
        if scheme.get("in") not in {"header", "query", "cookie"}:
            raise ValueError(
                "OpenAPI type='apiKey' requires 'in' to be header/query/cookie."
            )
        if not scheme.get("name"):
            raise ValueError("OpenAPI type='apiKey' requires 'name'.")

    if scheme_type == "oauth2" and not isinstance(scheme.get("flows"), Mapping):
        raise ValueError("OpenAPI type='oauth2' requires a 'flows' object.")

    if scheme_type == "openIdConnect" and not scheme.get("openIdConnectUrl"):
        raise ValueError("OpenAPI type='openIdConnect' requires 'openIdConnectUrl'.")


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

    _validate_openapi_security_scheme(scheme)
    return scheme_name, scheme


__all__ = [
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
