"""Utilities for core OAuth 2.0 Authorization Framework (RFC 6749).

This module provides helpers for validating token endpoint requests according
 to RFC 6749 Section 5.2. Validation can be toggled on or off via the
 ``enable_rfc6749`` setting in ``runtime_cfg.Settings``.
"""

from __future__ import annotations

from typing import Iterable, Mapping


class RFC6749Error(ValueError):
    """Error raised for RFC 6749 validation failures."""


def validate_grant_type(grant_type: str | None, allowed: Iterable[str]) -> None:
    """Validate presence and supported values of ``grant_type``.

    Raises:
        RFC6749Error: If ``grant_type`` is missing or not in ``allowed``.
    """
    if not grant_type:
        raise RFC6749Error("invalid_request")
    if grant_type not in set(allowed):
        raise RFC6749Error("unsupported_grant_type")


def validate_password_grant(form: Mapping[str, str]) -> None:
    """Ensure required parameters for the password grant are present.

    RFC 6749 §4.3 mandates both ``username`` and ``password`` parameters. Missing
    parameters result in ``invalid_request`` errors.
    """
    if "username" not in form or "password" not in form:
        raise RFC6749Error("invalid_request")
