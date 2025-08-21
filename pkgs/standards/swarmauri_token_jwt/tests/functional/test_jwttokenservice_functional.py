import base64
import pytest

from swarmauri_token_jwt import JWTTokenService
from swarmauri_core.keys import IKeyProvider, KeyRef


class DummyKeyProvider(IKeyProvider):
    def __init__(self) -> None:
        self.secret = b"secret"
        self.kid = "sym"
        self.version = 1

    async def get_key(
        self, kid: str, version: int | None = None, *, include_secret: bool = False
    ) -> KeyRef:
        material = self.secret if include_secret else None
        return KeyRef(kid=self.kid, version=self.version, material=material)

    async def jwks(self) -> dict:
        k = base64.urlsafe_b64encode(self.secret).rstrip(b"=").decode()
        return {"keys": [{"kty": "oct", "kid": f"{self.kid}.{self.version}", "k": k}]}


@pytest.mark.functional
@pytest.mark.asyncio
async def test_verify_with_audience() -> None:
    svc = JWTTokenService(DummyKeyProvider(), default_issuer="iss")
    token = await svc.mint({}, alg="HS256", kid="sym", audience="aud")
    claims = await svc.verify(token, issuer="iss", audience="aud")
    assert claims["aud"] == "aud"
