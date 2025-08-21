import base64
from swarmauri_core.crypto.types import KeyType

import pytest

from swarmauri_tokens_jwt import JWTTokenService
from swarmauri_core.keys import KeyRef, ExportPolicy, KeyUse


class DummyKeyProvider:
    def __init__(self) -> None:
        self.secret = b"secret"
        self.kid = "sym"
        self.version = 1

    async def get_key(
        self, kid: str, version: int | None = None, *, include_secret: bool = False
    ) -> KeyRef:
        material = self.secret if include_secret else None
        return KeyRef(
            kid=self.kid,
            version=self.version,
            type=KeyType.SYMMETRIC,
            uses=(KeyUse.SIGN,),
            export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
            material=material,
        )

    async def jwks(self) -> dict:
        k = base64.urlsafe_b64encode(self.secret).rstrip(b"=").decode()
        return {"keys": [{"kty": "oct", "kid": f"{self.kid}.{self.version}", "k": k}]}


@pytest.mark.unit
@pytest.mark.asyncio
async def test_mint_and_verify_roundtrip() -> None:
    svc = JWTTokenService(DummyKeyProvider(), default_issuer="iss")
    token = await svc.mint({"msg": "hi"}, alg="HS256", kid="sym")
    claims = await svc.verify(token, issuer="iss")
    assert claims["msg"] == "hi"
