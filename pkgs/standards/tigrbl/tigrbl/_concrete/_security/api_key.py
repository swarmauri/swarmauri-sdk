"""API key security scheme."""

from __future__ import annotations

from typing import Any, Sequence

from ...runtime.status.exceptions import HTTPException
from ...runtime.status.mappings import status
from ._base import OpenAPISecurityDependency


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
        headers = request.headers
        query = request.query_params
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
