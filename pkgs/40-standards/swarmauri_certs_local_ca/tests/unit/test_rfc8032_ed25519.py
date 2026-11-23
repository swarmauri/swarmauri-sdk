"""RFC 8032 Ed25519 certificate tests."""

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519

from swarmauri_certs_local_ca import LocalCaCertService
from swarmauri_core.crypto.types import ExportPolicy, KeyRef, KeyType, KeyUse


def _key() -> KeyRef:
    sk = ed25519.Ed25519PrivateKey.generate()
    pem = sk.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    return KeyRef(
        kid="ed",
        version=1,
        type=KeyType.ED25519,
        uses=(KeyUse.SIGN,),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        material=pem,
    )


@pytest.mark.unit
@pytest.mark.asyncio
async def test_self_signed_ed25519() -> None:
    svc = LocalCaCertService()
    key = _key()
    cert = await svc.create_self_signed(key, {"CN": "ed"})
    assert b"BEGIN CERTIFICATE" in cert
