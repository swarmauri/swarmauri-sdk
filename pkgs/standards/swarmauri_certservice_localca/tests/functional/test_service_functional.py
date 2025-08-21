import asyncio
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from swarmauri_certservice_localca import LocalCaCertService
from swarmauri_core.crypto.types import ExportPolicy, KeyRef, KeyType, KeyUse


def _keyref(name: str) -> KeyRef:
    sk = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pem = sk.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    return KeyRef(
        kid=name,
        version=1,
        type=KeyType.RSA,
        uses=(KeyUse.SIGN,),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        material=pem,
    )


async def _run() -> bool:
    ca_svc = LocalCaCertService()
    ca_key = _keyref("ca")
    leaf_key = _keyref("leaf")
    csr = await ca_svc.create_csr(leaf_key, {"CN": "leaf"})
    cert = await ca_svc.sign_cert(csr, ca_key, issuer={"CN": "ca"})
    result = await ca_svc.verify_cert(cert)
    return result["valid"] is True


@pytest.mark.functional
def test_end_to_end_flow() -> None:
    assert asyncio.run(_run())
