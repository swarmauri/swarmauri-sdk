"""RFC 5480 ECDSA P-256 certificate tests."""

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec

from swarmauri_certs_local_ca import LocalCaCertService
from swarmauri_core.crypto.types import ExportPolicy, KeyRef, KeyType, KeyUse


def _key() -> KeyRef:
    sk = ec.generate_private_key(ec.SECP256R1())
    pem = sk.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    return KeyRef(
        kid="ec",
        version=1,
        type=KeyType.EC,
        uses=(KeyUse.SIGN,),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        material=pem,
    )


@pytest.mark.unit
@pytest.mark.asyncio
async def test_self_signed_ecdsa() -> None:
    svc = LocalCaCertService()
    key = _key()
    cert = await svc.create_self_signed(key, {"CN": "ecdsa"})
    assert b"BEGIN CERTIFICATE" in cert
