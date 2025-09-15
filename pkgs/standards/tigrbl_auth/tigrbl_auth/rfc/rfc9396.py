"""Utilities for OAuth 2.0 Rich Authorization Requests (RFC 9396).

This module parses and validates the ``authorization_details`` request
parameter as defined by RFC 9396 section 2. Support for this feature can be
toggled via the ``TIGRBL_AUTH_ENABLE_RFC9396`` environment variable
(``settings.enable_rfc9396``).

See RFC 9396: https://www.rfc-editor.org/rfc/rfc9396
"""

from __future__ import annotations

from typing import Any, List
import json

from pydantic import BaseModel, ValidationError

from ..runtime_cfg import settings

RFC9396_SPEC_URL = "https://www.rfc-editor.org/rfc/rfc9396"


class AuthorizationDetail(BaseModel):
    """Minimal representation of an authorization detail item."""

    type: str


def parse_authorization_details(raw: str) -> List[AuthorizationDetail]:
    """Parse the RFC 9396 ``authorization_details`` parameter.

    Parameters
    ----------
    raw:
        A JSON string containing either a single authorization detail object
        or an array of such objects.

    Returns
    -------
    list[AuthorizationDetail]
        The parsed authorization details.

    Raises
    ------
    NotImplementedError
        If RFC 9396 support is disabled via runtime settings.
    ValueError
        If the input is not valid JSON or does not conform to the minimal
        requirements of RFC 9396.
    """

    if not settings.enable_rfc9396:
        raise NotImplementedError(
            f"authorization_details not enabled: {RFC9396_SPEC_URL}"
        )

    try:
        data: Any = json.loads(raw)
    except json.JSONDecodeError as exc:  # pragma: no cover - invalid JSON
        raise ValueError(
            f"authorization_details must be valid JSON: {RFC9396_SPEC_URL}"
        ) from exc

    if isinstance(data, dict):
        data = [data]
    if not isinstance(data, list):
        raise ValueError(
            f"authorization_details must be an object or array: {RFC9396_SPEC_URL}"
        )

    try:
        return [AuthorizationDetail.model_validate(item) for item in data]
    except ValidationError as exc:
        raise ValueError(f"invalid authorization_details: {RFC9396_SPEC_URL}") from exc


__all__ = [
    "AuthorizationDetail",
    "parse_authorization_details",
    "RFC9396_SPEC_URL",
]
