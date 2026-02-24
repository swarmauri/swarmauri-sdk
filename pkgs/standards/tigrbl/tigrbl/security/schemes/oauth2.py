"""OAuth2 security scheme."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from ._base import OpenAPISecurityDependency


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
