"""OpenID Connect security scheme."""

from __future__ import annotations

from typing import Any, Sequence

from ._base import OpenAPISecurityDependency


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
