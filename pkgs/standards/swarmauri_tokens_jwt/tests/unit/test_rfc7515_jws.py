import base64
import jwt
import pytest
from swarmauri_tokens_jwt import JWTTokenService
from swarmauri_core.crypto.types import (
    ExportPolicy,
    JWAAlg,
    KeyRef,
    KeyType,
    KeyUse,
)
from swarmauri_core.keys import IKeyProvider


class DummyKeyProvider(IKeyProvider):
    def __init__(self) -> None:
        self.secret = b"secret"
        self.kid = "sym"
        self.version = 1

    def supports(self) -> dict[str, list[str]]:
        return {}

    async def create_key(self, spec):  # pragma: no cover - unused
        raise NotImplementedError

    async def import_key(
        self, spec, material, *, public=None
    ):  # pragma: no cover - unused
        raise NotImplementedError

    async def rotate_key(
        self, kid: str, *, spec_overrides: dict | None = None
    ):  # pragma: no cover - unused
        raise NotImplementedError

    async def destroy_key(
        self, kid: str, version: int | None = None
    ) -> bool:  # pragma: no cover - unused
        return False

    async def get_key(
        self, kid: str, version: int | None = None, *, include_secret: bool = False
    ) -> KeyRef:
        material = self.secret if include_secret else None
        return KeyRef(
            kid=self.kid,
            version=self.version,
            type=KeyType.OPAQUE,
            uses=(KeyUse.SIGN,),
            export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
            material=material,
        )

    async def jwks(self) -> dict:
        k = base64.urlsafe_b64encode(self.secret).rstrip(b"=").decode()
        return {"keys": [{"kty": "oct", "kid": f"{self.kid}.{self.version}", "k": k}]}

    async def list_versions(self, kid: str):  # pragma: no cover - unused
        return (1,)

    async def get_public_jwk(
        self, kid: str, version: int | None = None
    ) -> dict:  # pragma: no cover - unused
        return {}

    async def random_bytes(self, n: int) -> bytes:  # pragma: no cover - unused
        raise NotImplementedError

    async def hkdf(
        self, ikm: bytes, *, salt: bytes, info: bytes, length: int
    ) -> bytes:  # pragma: no cover - unused
        raise NotImplementedError


@pytest.mark.unit
@pytest.mark.asyncio
async def test_rfc7515_header_alg() -> None:
    svc = JWTTokenService(DummyKeyProvider())
    token = await svc.mint({}, alg=JWAAlg.HS256, kid="sym")
    header = jwt.get_unverified_header(token)
    assert header["alg"] == JWAAlg.HS256.value
