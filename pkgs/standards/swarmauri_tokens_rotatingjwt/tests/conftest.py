import base64
import secrets
import pytest

from swarmauri_core.crypto.types import JWAAlg, KeyRef, KeyType
from swarmauri_core.key_providers.types import ExportPolicy, KeyUse, KeyAlg, KeySpec
from swarmauri_tokens_rotatingjwt import RotatingJWTTokenService


class DummyKeyProvider:
    def __init__(self) -> None:
        self.kid = "testkid"
        self.version = 1
        self.store = {1: secrets.token_bytes(32)}

    async def create_key(self, spec: KeySpec) -> KeyRef:
        return KeyRef(
            kid=self.kid,
            version=self.version,
            type=KeyType.SYMMETRIC,
            uses=(KeyUse.SIGN, KeyUse.VERIFY),
            export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
            material=self.store[self.version],
            tags={"alg": spec.alg.value},
        )

    async def get_key(
        self, kid: str, version: int | None = None, *, include_secret: bool = False
    ) -> KeyRef:
        v = version or self.version
        secret = self.store[v]
        return KeyRef(
            kid=self.kid,
            version=v,
            type=KeyType.SYMMETRIC,
            uses=(KeyUse.SIGN, KeyUse.VERIFY),
            export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
            material=secret if include_secret else None,
            tags={"alg": KeyAlg.AES256_GCM.value},
        )

    async def rotate_key(
        self, kid: str, *, spec_overrides: dict | None = None
    ) -> KeyRef:
        self.version += 1
        self.store[self.version] = secrets.token_bytes(32)
        return await self.get_key(kid, self.version, include_secret=True)

    async def get_public_jwk(self, kid: str, version: int) -> dict:
        secret = self.store[version]
        k = base64.urlsafe_b64encode(secret).rstrip(b"=").decode()
        return {"kty": "oct", "k": k, "kid": f"{kid}.{version}"}

    async def jwks(self) -> dict:
        keys = [await self.get_public_jwk(self.kid, v) for v in self.store]
        return {"keys": keys}


@pytest.fixture
def provider() -> DummyKeyProvider:
    return DummyKeyProvider()


@pytest.fixture
def service(provider) -> RotatingJWTTokenService:
    return RotatingJWTTokenService(provider, alg=JWAAlg.HS256)


@pytest.fixture
def rotating_service(provider) -> RotatingJWTTokenService:
    return RotatingJWTTokenService(provider, alg=JWAAlg.HS256, max_tokens_per_key=1)
