from __future__ import annotations

import base64
import os
from typing import Iterable, Mapping, Optional

import pytest
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    PrivateFormat,
    PublicFormat,
    NoEncryption,
)

from swarmauri_token_paseto_v4 import PasetoV4TokenService
from swarmauri_core.crypto.types import KeyRef, KeyType, KeyUse, ExportPolicy
from swarmauri_core.keys.IKeyProvider import IKeyProvider
from swarmauri_core.keys.types import KeyAlg


class DummyKeyProvider(IKeyProvider):
    def __init__(self) -> None:
        self.sk = Ed25519PrivateKey.generate()
        self.sym = os.urandom(32)
        self._refs = {
            "ed1": KeyRef(
                kid="ed1",
                version=1,
                type=KeyType.ED25519,
                uses=(KeyUse.SIGN, KeyUse.VERIFY),
                export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
                material=self.sk.private_bytes(
                    Encoding.PEM, PrivateFormat.PKCS8, NoEncryption()
                ),
                public=self.sk.public_key().public_bytes(
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
                material=self.sym,
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
                        self.sk.public_key().public_bytes(
                            Encoding.Raw, PublicFormat.Raw
                        )
                    )
                    .rstrip(b"=")
                    .decode("ascii"),
                }
            ]
        }

    def supports(self) -> Mapping[str, Iterable[str]]:  # pragma: no cover - not used
        return {}

    async def create_key(self, spec):  # pragma: no cover - not used
        raise NotImplementedError()

    async def import_key(
        self, spec, material, *, public=None
    ):  # pragma: no cover - not used
        raise NotImplementedError()

    async def rotate_key(
        self, kid, *, spec_overrides=None
    ):  # pragma: no cover - not used
        raise NotImplementedError()

    async def destroy_key(self, kid, version=None):  # pragma: no cover - not used
        raise NotImplementedError()

    async def get_key(self, kid, version=None, include_secret=False):
        return self._refs[kid]

    async def list_versions(self, kid):  # pragma: no cover - not used
        return (1,)

    async def get_public_jwk(self, kid, version=None):  # pragma: no cover - not used
        return self._jwks["keys"][0]

    async def jwks(self, *, prefix_kids: Optional[str] = None):
        return self._jwks

    async def random_bytes(self, n: int) -> bytes:  # pragma: no cover - not used
        return os.urandom(n)

    async def hkdf(
        self, ikm: bytes, *, salt: bytes, info: bytes, length: int
    ) -> bytes:  # pragma: no cover
        return HKDF(
            algorithm=hashes.SHA256(), length=length, salt=salt, info=info
        ).derive(ikm)


@pytest.fixture
def provider() -> DummyKeyProvider:
    return DummyKeyProvider()


@pytest.fixture
def token_service(provider: DummyKeyProvider) -> PasetoV4TokenService:
    return PasetoV4TokenService(provider, local_kids=["sym1"], default_issuer="issuer")
