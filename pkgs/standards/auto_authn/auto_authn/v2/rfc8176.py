"""Utilities for RFC 8176 - Authentication Method Reference Values.

The RFC defines standard values for the ``amr`` (Authentication Methods
Reference) claim. This module provides a minimal lookup helper that can be
enabled or disabled at runtime via the settings module.
"""

from __future__ import annotations

from typing import Dict

from .runtime_cfg import settings

RFC8176_SPEC_URL = "https://datatracker.ietf.org/doc/html/rfc8176"

_AMR_VALUES: Dict[str, str] = {
    "pwd": "Password",
    "otp": "One-Time Password",
    "sms": "SMS Challenge",
}


def amr_description(code: str) -> str:
    """Return the human-readable description for an ``amr`` code."""
    if not settings.enable_rfc8176:
        raise NotImplementedError("RFC 8176 support is disabled")
    return _AMR_VALUES.get(code, "Unknown")
