import base64

import pytest

from swarmauri_tokens_jwt import JWTTokenService
from swarmauri_core.crypto.types import JWAAlg, KeyType
from swarmauri_core.keys import (
    ExportPolicy,
    IKeyProvider,
    KeyRef,
    KeySpec,
    KeyUse,
)


class InMemoryKeyProvider(IKeyProvider):
    def __init__(self) -> None:
        self.secret = b"0123456789abcdef" * 2
        self.kid = "sym"
        self.version = 1

    def supports(self) -> dict[str, list[str]]:
        return {}

    async def create_key(self, spec: KeySpec) -> KeyRef:  # pragma: no cover - unused
        raise NotImplementedError

    async def import_key(  # pragma: no cover - unused
        self, spec: KeySpec, material: bytes, *, public: bytes | None = None
    ) -> KeyRef:
        raise NotImplementedError

    async def rotate_key(  # pragma: no cover - unused
        self, kid: str, *, spec_overrides: dict | None = None
    ) -> KeyRef:
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

    async def list_versions(
        self, kid: str
    ) -> tuple[int, ...]:  # pragma: no cover - unused
        return (self.version,)

    async def get_public_jwk(  # pragma: no cover - unused
        self, kid: str, version: int | None = None
    ) -> dict:
        return {}

    async def jwks(self) -> dict:
        k = base64.urlsafe_b64encode(self.secret).rstrip(b"=").decode()
        return {"keys": [{"kty": "oct", "kid": f"{self.kid}.{self.version}", "k": k}]}

    async def random_bytes(self, n: int) -> bytes:  # pragma: no cover - unused
        return b"\x00" * n

    async def hkdf(  # pragma: no cover - unused
        self, ikm: bytes, *, salt: bytes, info: bytes, length: int
    ) -> bytes:
        return b"\x00" * length


@pytest.mark.unit
@pytest.mark.example
@pytest.mark.asyncio
async def test_usage_mint_and_verify() -> None:
    svc = JWTTokenService(InMemoryKeyProvider(), default_issuer="issuer")
    token = await svc.mint({"sub": "alice"}, alg=JWAAlg.HS256, kid="sym")
    claims = await svc.verify(token, issuer="issuer")
    assert claims["sub"] == "alice"
