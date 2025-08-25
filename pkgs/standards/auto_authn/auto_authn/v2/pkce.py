"""PKCE utilities for RFC 8252 compliance.

This module implements the Proof Key for Code Exchange (PKCE) helpers
required by RFC 8252 for native applications.  It follows the rules laid
out in RFC 7636 §4.1 for generating and validating ``code_verifier``
strings and deriving ``code_challenge`` values using the ``S256``
transformation.
"""

from __future__ import annotations

import base64
import hashlib
import re
import secrets
from typing import Final

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


def create_code_challenge(verifier: str) -> str:
    """Derive an ``S256`` ``code_challenge`` from *verifier*.

    The verifier is first validated against the RFC 7636 §4.1 character and
    length requirements and then hashed using SHA-256 with the result encoded
    using base64url without padding, as required by RFC 7636 §4.2.
    """

    if not _VERIFIER_RE.fullmatch(verifier):
        raise ValueError("invalid code_verifier")
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    return base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")


def verify_code_challenge(verifier: str, challenge: str) -> bool:
    """Return ``True`` if *challenge* matches *verifier* using ``S256``."""

    try:
        expected = create_code_challenge(verifier)
    except ValueError:
        return False
    return secrets.compare_digest(expected, challenge)


__all__ = [
    "create_code_verifier",
    "create_code_challenge",
    "verify_code_challenge",
]
