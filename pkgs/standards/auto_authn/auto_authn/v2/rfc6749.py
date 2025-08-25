"""Minimal helpers for OAuth 2.0 Authorization Framework (RFC 6749).

This module offers basic validation for token requests and can be toggled via
``settings.enable_rfc6749`` in :mod:`runtime_cfg`.
"""

from __future__ import annotations

from typing import Mapping

from .runtime_cfg import settings


class RFC6749ComplianceError(ValueError):
    """Raised when a request violates RFC 6749 requirements."""


def validate_token_request(data: Mapping[str, str]) -> None:
    """Validate *data* representing a token request per RFC 6749.

    Checks for the presence of ``grant_type`` and ``client_id`` parameters as
    outlined in RFC 6749 Sections 4 and 2.3.1. Validation occurs only when
    ``settings.enable_rfc6749`` is ``True``.
    """
    if not settings.enable_rfc6749:
        return

    if "grant_type" not in data:
        raise RFC6749ComplianceError("'grant_type' is required per RFC 6749 section 4")
    if "client_id" not in data:
        raise RFC6749ComplianceError(
            "'client_id' is required per RFC 6749 section 2.3.1"
        )
