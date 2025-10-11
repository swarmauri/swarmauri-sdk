import json

import pytest

from swarmauri_keyprovider_local import LocalKeyProvider
from swarmauri_core.keys.types import KeySpec, KeyAlg, KeyClass, ExportPolicy, KeyUse
from swarmauri_core.crypto.types import KeyType


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_ed25519_jwk() -> None:
    kp = LocalKeyProvider()
    spec = KeySpec(
        klass=KeyClass.asymmetric,
        alg=KeyAlg.ED25519,
        uses=(KeyUse.SIGN, KeyUse.VERIFY),
        export_policy=ExportPolicy.PUBLIC_ONLY,
        encoding="PEM",
        private_format="PKCS8",
        public_format="SubjectPublicKeyInfo",
        encryption="NoEncryption",
    )
    ref = await kp.create_key(spec)
    jwk = await kp.get_public_jwk(ref.kid)
    assert jwk["kty"] == "OKP" and jwk["crv"] == "Ed25519"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_with_encoding_formats() -> None:
    kp = LocalKeyProvider()
    spec = KeySpec(
        klass=KeyClass.asymmetric,
        alg=KeyAlg.ED25519,
        uses=(KeyUse.SIGN, KeyUse.VERIFY),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        encoding="PEM",
        private_format="PKCS8",
        public_format="SubjectPublicKeyInfo",
        encryption="NoEncryption",
    )
    ref = await kp.create_key(spec)
    assert ref.public.startswith(b"-----BEGIN PUBLIC KEY-----")
    assert ref.material and ref.material.startswith(b"-----BEGIN PRIVATE KEY-----")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_local_provider_x25519_mlkem768() -> None:
    kp = LocalKeyProvider()
    spec = KeySpec(
        klass=KeyClass.asymmetric,
        alg=KeyAlg.X25519MLKEM768,
        uses=(KeyUse.ENCRYPT, KeyUse.DECRYPT),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
    )
    ref = await kp.create_key(spec)
    assert ref.type == KeyType.X25519_MLKEM768
    payload = json.loads(ref.public.decode("utf-8"))
    assert payload["kty"] == "X25519+ML-KEM-768"
    rotated = await kp.rotate_key(ref.kid)
    assert rotated.version == 2
    jwk = await kp.get_public_jwk(ref.kid)
    assert jwk["kty"] == "X25519+ML-KEM-768"
