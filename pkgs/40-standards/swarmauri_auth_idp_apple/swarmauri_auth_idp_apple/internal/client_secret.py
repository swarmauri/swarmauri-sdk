"""Utilities for constructing Apple Sign-in client secrets."""

from __future__ import annotations

import time
from dataclasses import dataclass

import jwt

APPLE_AUDIENCE = "https://appleid.apple.com"


@dataclass(frozen=True)
class AppleClientSecretFactory:
    """Build signed JWT client secrets for Apple identity flows."""

    team_id: str
    key_id: str
    client_id: str
    private_key_pem: bytes

    def build(self, ttl_seconds: int = 180 * 24 * 3600) -> str:
        """Create an ES256-signed client secret JWT."""

        now = int(time.time())
        headers = {"kid": self.key_id}
        payload = {
            "iss": self.team_id,
            "iat": now,
            "exp": now + ttl_seconds,
            "aud": APPLE_AUDIENCE,
            "sub": self.client_id,
        }
        return jwt.encode(
            payload, self.private_key_pem, algorithm="ES256", headers=headers
        )
