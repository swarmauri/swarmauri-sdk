"""Helpers for OAuth 2.0 Bearer Token Usage (RFC 6750).

This module extracts bearer tokens from HTTP requests according to
:rfc:`6750`. Support can be disabled entirely via ``settings.enable_rfc6750``.
Optional mechanisms for supplying the token in the URI query parameter or the
request body can also be toggled via settings to allow deployments to opt out
of these potentially insecure features.

See RFC 6750: https://www.rfc-editor.org/rfc/rfc6750
"""

from __future__ import annotations

from fastapi import Request
from typing import Final

from .runtime_cfg import settings

RFC6750_SPEC_URL: Final = "https://www.rfc-editor.org/rfc/rfc6750"


async def extract_bearer_token(request: Request, authorization: str) -> str | None:
    """Return the bearer token present in *request* if any.

    The function follows the extraction rules from RFC 6750:

    - The ``Authorization`` header uses a case-insensitive ``Bearer`` scheme.
    - Extraction occurs only when ``settings.enable_rfc6750`` is ``True``.
    - If ``settings.enable_rfc6750_query`` is ``True`` an ``access_token``
      parameter in the URI query is accepted.
    - If ``settings.enable_rfc6750_form`` is ``True`` an ``access_token``
      field in an ``application/x-www-form-urlencoded`` body is accepted.
    """

    if not settings.enable_rfc6750:
        return None

    parts = authorization.split()
    if len(parts) == 2 and parts[0].lower() == "bearer":
        return parts[1]

    if settings.enable_rfc6750_query:
        token = request.query_params.get("access_token")
        if token:
            return token

    if (
        settings.enable_rfc6750_form
        and request.method in {"POST", "PUT", "PATCH"}
        and "application/x-www-form-urlencoded"
        in request.headers.get("Content-Type", "")
    ):
        form = await request.form()
        token = form.get("access_token")
        if token:
            return token

    return None


__all__ = ["extract_bearer_token", "RFC6750_SPEC_URL"]
