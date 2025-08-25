"""PKCE utilities for RFC 7636 compliance.

This module implements the Proof Key for Code Exchange (PKCE)
requirements defined in :rfc:`7636`.  It provides helpers for creating
``code_verifier`` strings and deriving ``code_challenge`` values using the
``S256`` or ``plain`` transformations as described in RFC 7636 §§4.2 and 4.3.
The verification helpers respect :class:`~auto_authn.v2.runtime_cfg.Settings`
so deployments can enable or disable RFC 7636 enforcement at runtime.
"""

from __future__ import annotations

import base64
import hashlib
import re
import secrets
from typing import Final

from .runtime_cfg import settings

# Allowed characters for the code_verifier as defined by RFC 7636 §4.1
_VERIFIER_CHARSET: Final = (
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~"
)

# Regular expression to validate code_verifier values
_VERIFIER_RE: Final = re.compile(r"^[A-Za-z0-9\-._~]{43,128}$")


def create_code_verifier(length: int = 43) -> str:
    """Return a high-entropy ``code_verifier`` string.

    RFC 7636 §4.1 specifies that a ``code_verifier`` MUST be between 43 and
    128 characters and use only ``ALPHA / DIGIT / "-" / "." / "_" / "~"``.
    ``length`` defaults to the minimum 43 characters.
    """

    if not 43 <= length <= 128:
        raise ValueError("length must be between 43 and 128 characters")
    return "".join(secrets.choice(_VERIFIER_CHARSET) for _ in range(length))


def create_code_challenge(verifier: str, method: str = "S256") -> str:
    """Derive a ``code_challenge`` from *verifier*.

    ``method`` may be ``"S256"`` (the default) or ``"plain"`` as defined in
    RFC 7636 §4.2 and §4.3.  ``code_verifier`` values are validated per
    RFC 7636 §4.1 before transformation.  ``ValueError`` is raised for
    unsupported methods or invalid verifiers.
    """

    if not _VERIFIER_RE.fullmatch(verifier):
        raise ValueError("invalid code_verifier")
    if method == "plain":
        return verifier
    if method == "S256":
        digest = hashlib.sha256(verifier.encode("ascii")).digest()
        return base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")
    raise ValueError(f"unsupported code_challenge_method: {method}")


def verify_code_challenge(verifier: str, challenge: str, method: str = "S256") -> bool:
    """Return ``True`` if *challenge* matches *verifier*.

    Verification uses the specified ``method`` (``"S256"`` or ``"plain"``).
    When ``settings.enable_rfc7636`` is ``False`` the check is skipped and
    ``True`` is returned to allow clients that do not implement PKCE.
    """

    if not settings.enable_rfc7636:
        return True
    try:
        expected = create_code_challenge(verifier, method)
    except ValueError:
        return False
    return secrets.compare_digest(expected, challenge)


__all__ = [
    "create_code_verifier",
    "create_code_challenge",
    "verify_code_challenge",
]
