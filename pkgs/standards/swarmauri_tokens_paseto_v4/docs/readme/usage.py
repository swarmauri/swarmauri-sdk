import asyncio
import base64
import os
from typing import Iterable, Mapping, Optional

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    NoEncryption,
    PrivateFormat,
    PublicFormat,
)

from swarmauri_tokens_paseto_v4 import PasetoV4TokenService
from swarmauri_core.crypto.types import ExportPolicy, KeyRef, KeyType, KeyUse
from swarmauri_core.key_providers.IKeyProvider import IKeyProvider
from swarmauri_core.key_providers.types import KeyAlg


class InMemoryKeyProvider(IKeyProvider):
    def __init__(self) -> None:
        self._sk = Ed25519PrivateKey.generate()
        self._sym = os.urandom(32)
        self._refs = {
            "ed1": KeyRef(
                kid="ed1",
                version=1,
                type=KeyType.ED25519,
                uses=(KeyUse.SIGN, KeyUse.VERIFY),
                export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
                material=self._sk.private_bytes(
                    Encoding.PEM, PrivateFormat.PKCS8, NoEncryption()
                ),
                public=self._sk.public_key().public_bytes(
                    Encoding.PEM, PublicFormat.SubjectPublicKeyInfo
                ),
                tags={"alg": KeyAlg.ED25519.value},
            ),
            "sym1": KeyRef(
                kid="sym1",
                version=1,
                type=KeyType.SYMMETRIC,
                uses=(KeyUse.ENCRYPT, KeyUse.DECRYPT),
                export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
                material=self._sym,
                public=None,
                tags={"alg": KeyAlg.AES256_GCM.value},
            ),
        }
        self._jwks = {
            "keys": [
                {
                    "kty": "OKP",
                    "crv": "Ed25519",
                    "kid": "ed1",
                    "x": base64.urlsafe_b64encode(
                        self._sk.public_key().public_bytes(
                            Encoding.Raw, PublicFormat.Raw
                        )
                    )
                    .rstrip(b"=")
                    .decode("ascii"),
                }
            ]
        }

    def supports(self) -> Mapping[str, Iterable[str]]:
        return {}

    async def create_key(
        self, spec
    ):  # pragma: no cover - unused in the example
        raise NotImplementedError

    async def import_key(
        self, spec, material, *, public=None
    ):  # pragma: no cover
        raise NotImplementedError

    async def rotate_key(
        self, kid, *, spec_overrides=None
    ):  # pragma: no cover
        raise NotImplementedError

    async def destroy_key(self, kid, version=None):  # pragma: no cover
        raise NotImplementedError

    async def get_key(self, kid, version=None, include_secret=False):
        return self._refs[kid]

    async def list_versions(self, kid):  # pragma: no cover - unused
        return (1,)

    async def get_public_jwk(self, kid, version=None):  # pragma: no cover
        return self._jwks["keys"][0]

    async def jwks(self, *, prefix_kids: Optional[str] = None):
        return self._jwks

    async def random_bytes(self, n: int) -> bytes:  # pragma: no cover - unused
        return os.urandom(n)

    async def hkdf(
        self, ikm: bytes, *, salt: bytes, info: bytes, length: int
    ) -> bytes:  # pragma: no cover - unused
        return HKDF(
            algorithm=hashes.SHA256(), length=length, salt=salt, info=info
        ).derive(ikm)


async def main() -> None:
    provider = InMemoryKeyProvider()
    service = PasetoV4TokenService(
        provider,
        default_issuer="auth.example",
        local_kids=["sym1"],
    )

    public_token = await service.mint(
        {"role": "admin"},
        alg="v4.public",
        kid="ed1",
        audience="my-service",
    )
    verified_public = await service.verify(public_token, audience="my-service")
    print("Verified role:", verified_public["role"])

    local_token = await service.mint(
        {"feature": "beta"},
        alg="v4.local",
        kid="sym1",
    )
    verified_local = await service.verify(local_token)
    print("Local feature flag:", verified_local["feature"])


if __name__ == "__main__":
    asyncio.run(main())
