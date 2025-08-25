"""Device Authorization Grant helpers for RFC 8628 compliance.

This module implements utility helpers for the OAuth 2.0 Device Authorization
Grant as defined in :rfc:`8628`.  It provides functions for generating and
validating ``user_code`` values as well as creating high-entropy
``device_code`` strings.  The validation helpers may be disabled via runtime
configuration allowing deployments to opt-out of RFC 8628 enforcement.
"""

from __future__ import annotations

import re
import secrets
import string
from typing import Final

from .runtime_cfg import settings

# Character set for user_code per RFC 8628 §6.1 (uppercase letters and digits)
_USER_CODE_CHARSET: Final = string.ascii_uppercase + string.digits
_USER_CODE_RE: Final = re.compile(r"^[A-Z0-9]{8}$")


def generate_user_code(length: int = 8) -> str:
    """Return a user_code suitable for RFC 8628 §6.1.

    ``length`` defaults to the minimum 8 characters recommended by the spec
    and must be positive.  The resulting code uses only uppercase letters and
    digits for ease of transcription.
    """

    if length <= 0:
        raise ValueError("length must be positive")
    return "".join(secrets.choice(_USER_CODE_CHARSET) for _ in range(length))


def validate_user_code(code: str) -> bool:
    """Return ``True`` if *code* conforms to RFC 8628 §6.1.

    When ``settings.enable_rfc8628`` is ``False`` the check is skipped and
    ``True`` is returned to allow clients that do not implement the Device
    Authorization Grant.
    """

    if not settings.enable_rfc8628:
        return True
    return bool(_USER_CODE_RE.fullmatch(code))


def generate_device_code() -> str:
    """Return a high-entropy ``device_code`` per RFC 8628 §6.3."""

    # 32 bytes of randomness yields a 43-character URL-safe string
    return secrets.token_urlsafe(32)


__all__ = ["generate_user_code", "validate_user_code", "generate_device_code"]
