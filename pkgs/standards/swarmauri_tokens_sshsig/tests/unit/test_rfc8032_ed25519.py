import base64

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from swarmauri_tokens_sshsig import SshSigTokenService
from swarmauri_core.key_providers import IKeyProvider
from swarmauri_core.crypto.types import ExportPolicy, KeyRef, KeyType, KeyUse


class DummyKeyProvider(IKeyProvider):
    def __init__(self) -> None:
        self.sk = Ed25519PrivateKey.generate()
        self.pk = self.sk.public_key()
        self.kid = "ed"
        self.version = 1

    def supports(self) -> dict:
        return {}

    async def create_key(self, spec):
        raise NotImplementedError

    async def import_key(self, spec, material, *, public=None):
        raise NotImplementedError

    async def rotate_key(self, kid: str, *, spec_overrides: dict | None = None):
        raise NotImplementedError

    async def destroy_key(self, kid: str, version: int | None = None) -> bool:
        return True

    async def get_key(
        self, kid: str, version: int | None = None, *, include_secret: bool = False
    ) -> KeyRef:
        priv = (
            self.sk.private_bytes(
                serialization.Encoding.PEM,
                serialization.PrivateFormat.PKCS8,
                serialization.NoEncryption(),
            )
            if include_secret
            else None
        )
        pub = self.pk.public_bytes(
            serialization.Encoding.PEM,
            serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        return KeyRef(
            kid=self.kid,
            version=self.version,
            type=KeyType.ED25519,
            uses=(KeyUse.SIGN,),
            export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
            material=priv,
            public=pub,
        )

    async def list_versions(self, kid: str) -> tuple[int, ...]:
        return (self.version,)

    async def get_public_jwk(self, kid: str, version: int | None = None) -> dict:
        return {}

    async def jwks(self) -> dict:
        return {"keys": []}

    async def random_bytes(self, n: int) -> bytes:
        return b"\x00" * n

    async def hkdf(self, ikm: bytes, *, salt: bytes, info: bytes, length: int) -> bytes:
        return b"\x00" * length


@pytest.mark.unit
@pytest.mark.asyncio
async def test_ed25519_signature_length_rfc8032() -> None:
    kp = DummyKeyProvider()
    svc = SshSigTokenService(kp, default_issuer="iss")
    token = await svc.mint({}, alg="ssh-ed25519", kid="ed")
    sig_b64 = token.split(".")[-1]
    sig = base64.urlsafe_b64decode(sig_b64 + "==")
    assert len(sig) == 64
