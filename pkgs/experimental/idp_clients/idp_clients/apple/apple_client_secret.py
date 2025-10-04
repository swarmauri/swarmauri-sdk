from __future__ import annotations
import time, jwt
from dataclasses import dataclass

APPLE_AUD = "https://appleid.apple.com"

@dataclass(frozen=True)
class AppleClientSecretFactory:
    team_id: str       # Your Apple Developer Team ID (e.g., 'ABCD123456')
    key_id: str        # Key ID for your .p8 private key
    client_id: str     # Service ID (web) or app bundle ID
    private_key_pem: bytes  # contents of the .p8 key

    def build(self, ttl_seconds: int = 180*24*3600) -> str:
        now = int(time.time())
        headers = {"kid": self.key_id}
        payload = {
            "iss": self.team_id,
            "iat": now,
            "exp": now + ttl_seconds,
            "aud": APPLE_AUD,
            "sub": self.client_id,
        }
        # Apple requires ES256
        return jwt.encode(payload, self.private_key_pem, algorithm="ES256", headers=headers)
