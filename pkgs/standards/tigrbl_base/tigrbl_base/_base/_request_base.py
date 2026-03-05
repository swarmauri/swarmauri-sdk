from __future__ import annotations

from typing import Any
from urllib.parse import parse_qs

from tigrbl_core._spec.request_spec import RequestSpec


class RequestBase(RequestSpec):
    """Base request model behavior shared by concrete request implementations."""

    @classmethod
    def from_scope(
        cls,
        scope: dict[str, Any],
        receive: Any | None = None,
        *,
        app: Any | None = None,
        state: Any | None = None,
    ) -> "RequestBase":
        """Construct a base request from an ASGI scope and optional receive body."""

        del state  # reserved extension point

        method = str(scope.get("method", "GET"))
        path = str(scope.get("path", "/"))
        raw_query = scope.get("query_string", b"")
        if isinstance(raw_query, bytes):
            query_text = raw_query.decode("latin-1")
        else:
            query_text = str(raw_query)
        query = {
            key: [str(v) for v in values]
            for key, values in parse_qs(query_text, keep_blank_values=True).items()
        }

        headers: dict[str, str] = {}
        for key, value in scope.get("headers", []):
            headers[key.decode("latin-1").lower()] = value.decode("latin-1")

        return cls(
            method=method,
            path=path,
            headers=headers,
            query=query,
            path_params=dict(scope.get("path_params") or {}),
            body=b"",
            script_name=str(scope.get("root_path", "")),
            app=app,
        )


__all__ = ["RequestBase"]
