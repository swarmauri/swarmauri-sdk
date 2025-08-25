"""Policy helpers for user registration and authentication."""

from __future__ import annotations

import re
from typing import Optional

from .runtime_cfg import settings


class PasswordPolicyError(ValueError):
    """Raised when a password fails validation."""


def validate_password_strength(password: str) -> None:
    """Validate password against configured complexity requirements."""
    if len(password) < settings.password_min_length:
        raise PasswordPolicyError("password too short")
    if settings.password_regex and not re.fullmatch(settings.password_regex, password):
        raise PasswordPolicyError("password does not meet complexity requirements")


def validate_invite_code(invite_code: Optional[str]) -> None:
    """Validate *invite_code* against configured codes, if any."""
    codes = settings.invite_code_set
    if codes and (not invite_code or invite_code not in codes):
        raise ValueError("invalid invite code")
