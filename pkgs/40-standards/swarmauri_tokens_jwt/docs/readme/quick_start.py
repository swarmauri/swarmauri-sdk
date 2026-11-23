import asyncio
import base64
from swarmauri_tokens_jwt import JWTTokenService
from swarmauri_core.key_providers import (
    ExportPolicy,
    IKeyProvider,
    KeyRef,
    KeyUse,
)
from swarmauri_core.crypto.types import JWAAlg, KeyType


class InMemoryKeyProvider(IKeyProvider):
    def __init__(self) -> None:
        self.secret = b"secret"
        self.kid = "sym"
        self.version = 1

    def supports(self) -> dict[str, list[str]]:
        return {}

    async def create_key(self, spec):
        raise NotImplementedError

    async def import_key(self, spec, material, *, public=None):
        raise NotImplementedError

    async def rotate_key(self, kid, *, spec_overrides=None):
        raise NotImplementedError

    async def destroy_key(self, kid, version=None) -> bool:
        return False

    async def get_key(
        self, kid, version=None, *, include_secret=False
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

    async def list_versions(self, kid):
        return (self.version,)

    async def get_public_jwk(self, kid, version=None):
        return {}

    async def jwks(self) -> dict:
        k = base64.urlsafe_b64encode(self.secret).rstrip(b"=").decode()
        return {
            "keys": [
                {"kty": "oct", "kid": f"{self.kid}.{self.version}", "k": k}
            ]
        }

    async def random_bytes(self, n: int) -> bytes:
        return b"\x00" * n

    async def hkdf(
        self, ikm: bytes, *, salt: bytes, info: bytes, length: int
    ) -> bytes:
        return b"\x00" * length


async def main() -> None:
    svc = JWTTokenService(InMemoryKeyProvider(), default_issuer="issuer")
    token = await svc.mint(
        {"sub": "alice"},
        alg=JWAAlg.HS256,
        kid="sym",
        lifetime_s=600,  # override the default one-hour lifetime if needed
    )
    claims = await svc.verify(token, issuer="issuer")
    assert claims["sub"] == "alice"


asyncio.run(main())
