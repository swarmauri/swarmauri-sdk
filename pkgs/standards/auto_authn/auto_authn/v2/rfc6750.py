"""Helpers for OAuth 2.0 Bearer Token usage (RFC 6750).

These utilities centralize token extraction logic and can be toggled via
``settings.enable_rfc6750``.
"""

from __future__ import annotations

from fastapi import Request

from .runtime_cfg import settings


async def get_bearer_token(request: Request, authorization: str) -> str | None:
    """Return the bearer token from header, query or form body.

    When ``settings.enable_rfc6750`` is ``False`` only the strict
    ``Authorization: Bearer <token>`` header is honored.
    """
    scheme, _, param = authorization.partition(" ")
    if scheme == "Bearer":
        return param

    if not settings.enable_rfc6750:
        return None

    if scheme.lower() == "bearer":
        return param

    if token := request.query_params.get("access_token"):
        return token

    if request.method in {"POST", "PUT", "PATCH"}:
        content_type = request.headers.get("content-type", "")
        if content_type.startswith("application/x-www-form-urlencoded"):
            form = await request.form()
            token = form.get("access_token")
            if isinstance(token, str):
                return token

    return None
