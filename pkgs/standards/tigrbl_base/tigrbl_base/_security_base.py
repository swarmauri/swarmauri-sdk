"""Core OpenAPI security scheme primitives."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

_VALID_SECURITY_SCHEME_TYPES = {
    "http",
    "apiKey",
    "oauth2",
    "openIdConnect",
    "mutualTLS",
}


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
        validate_openapi_security_scheme(self._scheme)

    def openapi_security_scheme(self) -> dict[str, Any]:
        return dict(self._scheme)

    def openapi_security_requirement(self) -> dict[str, list[str]]:
        return {self.scheme_name: list(self._scopes)}

    def __call__(self, request: Any) -> Any | None:
        return None


def validate_openapi_security_scheme(scheme: Mapping[str, Any]) -> None:
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
