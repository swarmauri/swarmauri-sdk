"""Utilities for OAuth 2.0 Bearer Token Usage (RFC 6750)."""

from __future__ import annotations

from fastapi import Request


async def extract_bearer_token(
    request: Request | None,
    authorization_header: str,
) -> str | None:
    """Return bearer token from *authorization_header* or *request*.

    This implements the token transmission methods defined in RFC 6750:

    * Authorization header (case-insensitive ``Bearer`` scheme)
    * URI query parameter ``access_token``
    * Form-encoded body parameter ``access_token``
    """

    scheme, _, token = authorization_header.partition(" ")
    if scheme.lower() == "bearer" and token:
        return token

    if request is None:
        return None

    if token := request.query_params.get("access_token"):
        return token

    if request.method in {
        "POST",
        "PUT",
        "PATCH",
    } and "application/x-www-form-urlencoded" in request.headers.get(
        "content-type", ""
    ):
        form = await request.form()
        token = form.get("access_token")
        if token:
            return token

    return None
