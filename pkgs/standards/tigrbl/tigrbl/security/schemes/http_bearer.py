"""HTTP bearer security scheme."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

from ...runtime.status.exceptions import HTTPException
from ...runtime.status.mappings import status
from ._base import OpenAPISecurityDependency


@dataclass(frozen=True)
class HTTPAuthorizationCredentials:
    scheme: str
    credentials: str


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
