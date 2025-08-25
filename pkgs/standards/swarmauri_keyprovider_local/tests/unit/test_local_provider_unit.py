import pytest

from swarmauri_keyprovider_local import LocalKeyProvider
from swarmauri_core.keys.types import KeySpec, KeyAlg, KeyClass, ExportPolicy, KeyUse


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
