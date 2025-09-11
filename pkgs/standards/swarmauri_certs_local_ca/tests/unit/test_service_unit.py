import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from swarmauri_certs_local_ca import LocalCaCertService
from swarmauri_core.crypto.types import ExportPolicy, KeyRef, KeyType, KeyUse


def _make_keyref() -> KeyRef:
    sk = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pem = sk.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    return KeyRef(
        kid="test",
        version=1,
        type=KeyType.RSA,
        uses=(KeyUse.SIGN,),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        material=pem,
    )


@pytest.mark.unit
@pytest.mark.asyncio
async def test_self_signed_and_parse() -> None:
    svc = LocalCaCertService()
    key = _make_keyref()
    cert = await svc.create_self_signed(key, {"CN": "unit"})
    parsed = await svc.parse_cert(cert)
    assert parsed["subject"].startswith("CN=unit")
